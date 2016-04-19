#!/LAPPTIV/upshield/bin/python
#coding=utf-8
import os
import sys
import base64
from Crypto.Cipher import AES
from Crypto.Cipher import DES

def decryptAES(file,text):
	print "AES" 
	return text

def decrypt3DES(file,text):
	print "3DES"
	return text


fo = open("boot.properties", "r")
for line in fo.readlines():
	line = line.strip()
	if line.startswith("#"):
		continue
	elif line.startswith("username="):
		euser=line.replace("username=","")
		if euser.startswith("{AES}"):
			user=decryptAES("SerializedSystemIni.dat",euser.replace("{AES}",""))
		elif euser.startswith("{3DES}"):
			user=decrypt3DES("SerializedSystemIni.dat",euser.replace("{3DES}",""))
		else:
			print "invalid username:%s" %(euser)
	elif line.startswith("password="):
		epwd=line.replace("password=","")
		if epwd.startswith("{AES}"):
			pwd=decryptAES("SerializedSystemIni.dat",epwd.replace("{AES}",""))
		elif epwd.startswith("{3DES}"):
			pwd=decrypt3DES("SerializedSystemIni.dat",epwd.replace("{3DES}",""))
		else:
			print "invalid username:%s" %(euser)
print "user=%s,pwd=%s" %(user,pwd)


