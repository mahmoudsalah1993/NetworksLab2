import socket
import signal

from packet import *

UDP_IP = "127.0.0.1"
global udp_port
udp_port = 9000

TIMEOUT_VALUE = 3


def signal_handler(signum, frame):
	raise Exception("Timed out!")

#Ack received pkt
def ack(seqno):
	global udp_port
	ack_pkt = packet(0, 0, seqno, b'')
	sock.sendto(ack_pkt.toBuffer(), (UDP_IP, udp_port))

def request_file(FILE_NAME):
	while True:
		#signal.signal(signal.SIGALRM, signal_handler)
		#signal.alarm(TIMEOUT_VALUE)
		try:
			global udp_port
			p = packet(0, len(FILE_NAME), 0, FILE_NAME.encode())
			sock.sendto(p.toBuffer(), (UDP_IP, udp_port))
			print("file request sent")

			data, addr = sock.recvfrom(1024)
			
			ack_pkt = parse_packet(data)
			
			# check if ACK
			#if ack_pkt.length == 0 and ack_pkt.seqno == 0:
			if ack_pkt.length == 0:
				udp_port = ack_pkt.seqno
				print("Received Ack")
				break

		except socket.timeout:
			print("Timed out!")

def receive_file(file_name):
	#sock.settimeout(10)
	f = open(file_name, "wb")
	expected_seqno = 1
	print('start receiving data...')
	while True:
		#data = sock.recvfrom(1024)
		try:
			# write data to file
			data, addr = sock.recvfrom(1024)
			print("chunk received")
			pkt = parse_packet(data)
			if(pkt.seqno != expected_seqno):
				print("Unexpected seqno ",pkt.seqno)
				ack(pkt.seqno-1)
				continue
			expected_seqno += 1
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
	sock.bind(("127.0.0.1", 4321))
	print("port: ",4321)
	request_file("p.MKV")
	receive_file("a.MKV")
	sock.close()