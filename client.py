import socket
import signal

from packet import *

UDP_IP = "127.0.0.1"
UDP_PORT = 9000

TIMEOUT_VALUE = 3


def signal_handler(signum, frame):
	raise Exception("Timed out!")

#Ack received pkt
def ack(seqno):
	ack_pkt = packet(0, 0, seqno, b'')
	sock.sendto(ack_pkt.toBuffer(), (UDP_IP, UDP_PORT))

def request_file(FILE_NAME):
	while True:
		#signal.signal(signal.SIGALRM, signal_handler)
		#signal.alarm(TIMEOUT_VALUE)
		try:
			p = packet(0, len(FILE_NAME), 0, FILE_NAME.encode())
			sock.sendto(p.toBuffer(), (UDP_IP, UDP_PORT))
			print("file request sent")

			data, addr = sock.recvfrom(1024)
			
			ack_pkt = parse_packet(data)
			
			# check if ACK
			if ack_pkt.length == 0 and ack_pkt.seqno == 0:
				print("Received Ack")
				break

		except socket.timeout:
			print("Timed out!")

def receive_file(file_name):
	#sock.settimeout(10)
	f = open(file_name, "wb")
	print('start receiving data...')
	while True:
		#data = sock.recvfrom(1024)
		try:
			# write data to file
			data, addr = sock.recvfrom(1024)
			print("chunk received", data)
			pkt = parse_packet(data)
			f.write(pkt.data)
			ack(pkt.seqno)
			print("ACK ", pkt.seqno)
			if(pkt.length == 0):
				break
		except socket.timeout:
			print("Timed out!")
	f.close()
	print('Successfully get the file')


if __name__ == "__main__":
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.settimeout(TIMEOUT_VALUE)	#set recv timeout ==> exception socket.timeout
	request_file("p.jpg")
	receive_file("a.jpg")
	sock.close()