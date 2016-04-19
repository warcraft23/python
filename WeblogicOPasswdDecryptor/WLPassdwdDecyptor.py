__author__ = 'Edward'


#coding = utf-8
import os
import sys
import base64
from Crypto.Cipher import DES3
from Crypto.Cipher import AES
from Crypto.Hash import SHA
from Crypto.Cipher import ARC2
import struct

# Its function has been tested
def readBytes(stream):
    length = struct.unpack('b', stream.read(1))[0]
    return stream.read(length)

def decryptAES(file, ciphertext):
    # print "AES"
    text = b''
    # base64_decoded_text = base64.b64decode(ciphertext)
    base64_decoded_text =ciphertext.decode('base64')
    key = "0xccb97558940b82637c8bec3c770f86fa3a391a56"


    #read salt from file
    fo = open(file, "rb")
    salt = readBytes(fo)

    version = struct.unpack('b', fo.read(1))[0]

    # read encryptionKey from file
    if version != -1:
        encrypt_key = readBytes(fo)
        if version >=2:
            encrypt_key = readBytes(fo)

    # var 'key2key' means RC2 key to AES key
    print "encrypt_key(%d): %s" % (len(encrypt_key), encrypt_key.encode('hex'))
    hasher = SHA.new()
    hasher.update(salt)
    hasher.update(key)
    # hasher.update(key)
    # hasher.update(salt)
    key2key = hasher.digest()
    print key2key.encode('hex')

    for i in range(1, 5):
        hasher = SHA.new()
        hasher.update(key2key)
        key2key = hasher.digest()
        print key2key.encode('hex')

    print "key2key len:", len(key2key)
    print "key2key:", key2key.encode("hex")

    print encrypt_key[:8].encode('hex')
    rc2 = ARC2.new(key2key[8:], ARC2.MODE_CBC, key2key[:8])

    print encrypt_key[8:].encode('hex')
    key = rc2.decrypt(encrypt_key)

    print "key:", key.encode('hex')


    # iv = ciphertext.index(0, 16)
    # ciphertext2 = ciphertext.index(16)
    #
    # AESCipher = AES.new(key, AES.MODE_CBC, iv)
    #
    # text = AESCipher.decrypt(ciphertext2)

    fo.close()
    return text

def decrypt3DES(file,text):
    print "3DES"
    return text


fo = open("boot.properties", "r")
user = ""
pwd = ""
for line in fo.readlines():
    line = line.strip()
    if line.startswith("#"):
        continue
    elif line.startswith("username="):
        encrypt_user = line.replace("username=", "")
        if encrypt_user.startswith("{AES}"):
            user = decryptAES("SerializedSystemIni.dat", encrypt_user.replace("{AES}", ""))
        elif encrypt_user.startswith("{3DES}"):
            user = decrypt3DES("SerializedSystemIni.dat", encrypt_user.replace("{3DES}", ""))
        else:
            print "invalid username:%s" %( encrypt_user )
    elif line.startswith("password="):
        encrypt_pwd = line.replace("password=", "")
        if encrypt_pwd.startswith("{AES}"):
            pwd = decryptAES("SerializedSystemIni.dat", encrypt_pwd.replace("{AES}", ""))
        elif encrypt_pwd.startswith("{3DES}"):
            pwd = decrypt3DES("SerializedSystemIni.dat", encrypt_pwd.replace("{3DES}", ""))
        else:
            print "invalid username:%s" %(encrypt_user)
print "user = %s, pwd = %s" % (user, pwd)