import socket
import time
from packet import *
from threading import Thread 
#from SocketServer import ThreadingMixIn

# Multithreaded Python server : TCP Server Socket Thread Pool
class ClientThread(Thread): 
 
	def __init__(self,file_name,addr): 
		Thread.__init__(self) 
		self.file_name = file_name 
		self.addr = addr 
		print ("[+] New thread started for ",addr)
 
	def run(self): 
		self.send_file(self.file_name, self.addr) 

	def send_file(self,file_name, addr):
		print('start sending file', file_name, 'to client')
		time.sleep(1)
		f = open(file_name, "rb")
		#Start sending the file
		seqno = 0
		l = f.read(512)
		print("Start sending the file:")

		client_addr = ''
		while (l):
			#time.sleep(2)
			seqno += 1
			pkt = packet(0, len(l), seqno, l)

			while True:	#send pkt and wait for ACK
				try:
					sock.sendto(pkt.toBuffer(), addr)
					#sock.sendto(pkt.toBuffer(), addr)
					print("Pkt sent ", seqno)

					data, addr = sock.recvfrom(1024)
					client_addr = addr

					ack_pkt = parse_packet(data)
					# check if ACK
					if (ack_pkt.length == 0 and ack_pkt.seqno == seqno):
						print("Received Ack")
						break
					#print(ack_pkt.seqno," != ", seqno)
				except socket.timeout:
					print("Timed out!")
			l = f.read(512)
		print('sending package with data_len = 0')
		sock.sendto(packet(0, 0, seqno + 1, b'').toBuffer(), client_addr)
		
		f.close()
		print("-------File sent---------")


TIMEOUT_VALUE = 3
UDP_IP = "127.0.0.1"
UDP_PORT = 9000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(TIMEOUT_VALUE)
threads = []

print("Socket started:")

#Ack received pkt
def ack(seqno, addr):
	ack_pkt = packet(0, 0, seqno, b'')
	sock.sendto(ack_pkt.toBuffer(), addr)


if __name__ == "__main__":
	while True:
		try:
			p, addr = sock.recvfrom(1024)
			print("received packet: ", p)
			p = parse_packet(p)
			print(p.chksum)
			print(p.length)
			print(p.seqno)
			print((p.data).decode('ascii'))
			ack(p.seqno, addr)
			print("ACK", p.seqno)

			if p.seqno == 0: # this is actually a file request
				newthread = ClientThread((p.data).decode('ascii'),addr) 
				newthread.start()
				threads.append(newthread)
			
			for t in threads: 
				t.join() 
		except socket.timeout:
			pass
