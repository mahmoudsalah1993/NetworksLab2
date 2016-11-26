import socket
import time
from packet import *

TIMEOUT_VALUE = 3
UDP_IP = "127.0.0.1"
UDP_PORT = 9000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

sock.settimeout(TIMEOUT_VALUE)
print("Socket started:")

#Ack received pkt
def ack(seqno, addr):
	ack_pkt = packet(0, 0, seqno, b'')
	sock.sendto(ack_pkt.toBuffer(), addr)

def send_file(file_name, addr):
	print('start sending file', file_name, 'to client')
	time.sleep(2)
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
	sock.sendto(packet(0, 0, seqno, b'').toBuffer(), client_addr)
	
	f.close()
	print("-------File sent---------")


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
			send_file((p.data).decode('ascii'), addr)#Send file to server
		except socket.timeout:
			pass
