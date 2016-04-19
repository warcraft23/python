#!/usr/bin/python
#coding=utf-8
from scapy.all import *
import getopt
import sys
from scapy.layers import inet

packet_count = 0
target = ""
port = 0
victim= ""
interface = "en0"

#数据包回调函数
def packet_callback(packet)
    global target
    global victim
    print packet.show()
    if packet.haslayer(inet.IP):
        print "I have IP part!"

        if packet.haslayer(inet.TCP):
            print "I have TCP part!"
        if packet[inet.IP].dst == target:


def usage():
    print "mySniffer.py -h"
    print "mySniffer.py --help"
    print "mySniffer.py -i en0 -t 192.168.1.1 -p 9999 -n 10"
    print "mySniffer.py --interface en0 --target 192.168.1.1 --port 9999 --number 10"
    sys.exit(0)

def main():
    global packet_count
    global target
    global port
    global interface

    if not len(sys.argv[1:]):
        usage()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:n:p:t:", ["help", "interface", "number", "port", "target"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-i", "--interface"):
            interface = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-n", "--number"):
            packet_count = int(a)
        else:
            assert False, "Unhandled Option"

    print "[*] Eth is %s" % interface

    print "[*] The Number of Packets is %d" % packet_count


    if target == "":
        usage()
    else:
       print "[*] Target IP is %s" % target

    if port == 0:
        usage()
    else:
        print "[*] Target port is %d" % port

    #关闭输出
    conf.verb = 0

    print "[*] Starting Sniffer for %d packets to IP:%s" % (packet_count, target)

    bpf_filter = "(ip host %s) and (tcp port %d)" % (target, port)
    # bpf_filter = "ip host %s" % target

    if packet_count == 0:
        packets = sniff(prn=packet_callback, filter=bpf_filter, iface=interface)
    else:
        packets = sniff(prn=packet_callback, count=packet_count, filter=bpf_filter, iface=interface)

    #######################
    # 这里添加对包的修改函数 #
    #######################

    if packets is None:
        print "Sniff Error!"
    else:
        wrpcap("arpspoof.pcap", packets)
    # print "2"

main()
