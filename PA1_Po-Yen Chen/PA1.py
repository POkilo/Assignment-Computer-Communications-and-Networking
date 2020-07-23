import socket
import random
import re
import string 
import socket 
import binascii
from codecs import *

sAddress = '8.8.8.8'
Port = 53

def QueryToDgram(query):
	# ==============header=====6x16 bits=======
	randomId = '00'
	I = random.randint(0,255)
	randomId+= hex(I)[2:]

	rest = '' 
	for i in range(0,3):
		rest+='0000'
	header = randomId + '01000001' + rest
	# temp = '00000001000000000000000000000001'		
	# ==============question====3x16 bits=======
	Qname = ''
	for i in query.split('.'):
		Qname += (str(hex(len(i)/16))[2:]+str(hex(len(i)%16))[2:])			
		for j in i:
			Qname += encode(j,'hex')
	Qtype = '00010001'
	question = Qname+'00'+Qtype
	# ============================================
	return header + question
	

def DgramToResponse(message):
	try:
		print '======================Header====================='
		plain = re.findall('[0-9a-f][0-9a-f]',encode(message,'hex'))
		# ============header==============
		# go through the header and check 
		# what sections the response has
		# 24 hex num
		header = {}
		print 'headerID :','0x'+plain[0]+plain[1]
		flag = bin(int(plain[2],16)).zfill(8)[2:]+bin(int(plain[3],16)).zfill(8)[2:]
		print 'headerQR :',int(flag[0:1],2) #1
		print 'headerOpcode :',int(flag[2:5],2) #3
		print 'headerAA :',int(flag[5:6],2) #1
		print 'headerTC :',int(flag[6:7],2) #1
		print 'headerRD :',int(flag[7:8],2) #1
		print 'headerRA :',int(flag[8:9],2) #1
		print 'headerZ :',int(flag[9:12],2) #3
		print 'headerRcode :',int(flag[12:16],2) #4
		qd = int(plain[4]+plain[5],16)
		an = int(plain[6]+plain[7],16)
		ns = int(plain[8]+plain[9],16)
		ar = int(plain[10]+plain[11],16)
		print 'QDCOUNT :',qd
		print 'ANCOUNT :',an
		print 'NSCOUNT :',ns
		print 'ARCOUNT :',ar


		plain = plain[12:]	
		name = ''
		# ===========Question=============
		if qd!=0:
			print '\n====================Question====================='
			cut = 0
			for index,i in enumerate(plain):
				if (plain[index]=='00' and plain[index+1]=='00'):
					cut = index
					break
			ind = 0
			qname = ''
			while 1:
				for i in range(int(plain[ind],16)):
					ind+=1
					qname+=decode(plain[ind].strip(),'hex')	
				qname+='.'
				ind+=1
				if ind >= cut:
					break
			print 'QNAME :',qname
			name = qname
			plain = plain[cut+1:]	
			print 'QTYPE :',hex(int(plain[0]+plain[1],16))
			print 'QCLASS :',hex(int(plain[2]+plain[3],16))
			plain = plain[4:]
		# ============Answer==============
		if an!=0:
			new = name
			print '\n======================Answer====================='
			for i in range(an):
				print '\n######Answer',i+1,'#######'
				print 'NAME :',new,'(',plain[0],plain[1],')'
				print 'TYPE :',hex(int(plain[2]+plain[3],16))
				print 'CLASS :',hex(int(plain[4]+plain[5],16))
				print 'TTL(time to live) :',int(plain[6]+plain[7]+plain[8]+plain[9],16)
				print 'RDLENGTH :',int(plain[10]+plain[11],16)
				address = str(int(plain[12],16))+'.'+str(int(plain[13],16))+'.'+str(int(plain[14],16))+'.'+str(int(plain[15],16))
				if (int(plain[2]+plain[3],16)==1):
					print 'RDATA :',address,'  ##resolved IP address##'
					plain = plain[16:]
					continue

				# if type is not A
				plain = plain[12:]
				cut = 0
				for index,i in enumerate(plain):
					if (plain[index]=='00'):
						cut = index
						break
				ind = 0
				d = ''
				while 1:
					for i in range(int(plain[ind],16)):
						ind+=1
						d+=decode(plain[ind].strip(),'hex')	
					d+='.'
					ind+=1
					if ind >= cut:
						break
				print 'RDATA :',d
				new = d
				plain = plain[cut+1:]
		# ============Anutho==============
		if ns!=0:
			new = name
			print '\n======================Autho====================='
			for i in range(ns):
				print 'NAME :','root','(',plain[0],')'
				print 'TYPE :',hex(int(plain[1]+plain[2],16))
				print 'CLASS :',hex(int(plain[3]+plain[4],16))
				print 'TTL(time to live) :',int(plain[5]+plain[6]+plain[7]+plain[8],16)
				print 'RDLENGTH :',int(plain[9]+plain[10],16)
				# if type is not A
				plain = plain[11:]
				cut = 0
				for index,i in enumerate(plain):
					if (plain[index]=='00'):
						cut = index
						break
				ind = 0
				d = ''
				while 1:
					for i in range(int(plain[ind],16)):
						ind+=1
						d+=decode(plain[ind].strip(),'hex')	
					d+='.'
					ind+=1
					if ind >= cut:
						break
				print 'RDATA :',d
				new = d
				plain = plain[cut+1:]
				
		# ===========Addition=============
		if ar!=0:
			new = name
			print '\n====================Addition====================='
			for i in range(ar):
				print 'NAME :',new,'(',plain[0],plain[1],')'
				print 'TYPE :',hex(int(plain[2]+plain[3],16))
				print 'CLASS :',hex(int(plain[4]+plain[5],16))
				print 'TTL(time to live) :',int(plain[6]+plain[7]+plain[8]+plain[9],16)
				print 'RDLENGTH :',int(plain[10]+plain[11],16)
				address = str(int(plain[12],16))+'.'+str(int(plain[13],16))+'.'+str(int(plain[14],16))+'.'+str(int(plain[15],16))
				if (int(plain[2]+plain[3],16)==1):
					print 'RDATA :',address,'  ##resolved IP address##'
					plain = plain[16:]
					continue

				# if type is not A
				plain = plain[12:]
				cut = 0
				for index,i in enumerate(plain):
					if (plain[index]=='00'):
						cut = index
						break
				ind = 0
				d = ''
				while 1:
					for i in range(int(plain[ind],16)):
						ind+=1
						d+=decode(plain[ind].strip(),'hex')	
					d+='.'
					ind+=1
					if ind >= cut:
						break
				print 'RDATA :',d
				new = d
				plain = plain[cut+1:]
		print '=================================================\n\n'
	except Exception,e:
		print '\n\n !!!!!!bad request please try again!!!!!!'
		pass

	return

def main():

	while 1:	
		query = raw_input('$> dns-client ').strip()
		if query == 'q':
			break
		if query == '':
			continue
		print '\n\nPreparing DNS query...'
		qDgram = decode(QueryToDgram(query).strip(),'hex')
		print 'Contacting DNS server...'
		cSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		cSocket.connect((sAddress, Port))
		cSocket.setblocking(0)
		cSocket.settimeout(3)
		# 3 attempts
		print 'Sending DNS query...'
		for i in range(0,3):
			try:
				print '<attemp', i+1,'> please wait...'
				cSocket.sendall(qDgram)
				response = cSocket.recv(1024)
				print 'DNS response received (attempt ',i+1,' of 3) \n'
				print 'Processing DNS response...\n'
				DgramToResponse(response)
				
				break

			except Exception:
				pass

		cSocket.close()

if __name__ == "__main__":
	main()

