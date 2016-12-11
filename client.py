import socket
from packet import *
from random import randint

UDP_IP = "127.0.0.1"
UDP_PORT = 9010
TIMEOUT_VALUE = 3
plp = 0.1

def signal_handler(signum, frame):
	raise Exception("Timed out!")

#Ack received pkt
def ack(seqno):
	global udp_port
	ack_pkt = packet(0, 0, seqno, b'')
	sock.sendto(ack_pkt.toBuffer(), (UDP_IP, UDP_PORT))

def request_file(FILE_NAME):
	while True:
		#signal.signal(signal.SIGALRM, signal_handler)
		#signal.alarm(TIMEOUT_VALUE)
		try:
			global UDP_PORT
			p = packet(0, len(FILE_NAME), 0, FILE_NAME.encode())
			sock.sendto(p.toBuffer(), (UDP_IP, UDP_PORT))
			print("file request sent")

			data, addr = sock.recvfrom(1024)
			
			ack_pkt = parse_packet(data)
			
			# check if ACK
			#if ack_pkt.length == 0 and ack_pkt.seqno == 0:
			if ack_pkt.length == 0 and ack_pkt.seqno == 0 and ack_pkt.chksum == ack_pkt.checksum():
				print("Received Ack")
				print('change server port from:', UDP_PORT)
				UDP_PORT = addr[1]
				print('to', UDP_PORT)
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
				print("Unexpected seqno: ",pkt.seqno, "Expecting: ",expected_seqno)
				ack(expected_seqno -1)
				continue
			if(pkt.chksum != pkt.checksum()):
				print("wrong checksum Expected: ", pkt.chksum, " calculated: ", pkt.checksum)
				continue
			expected_seqno += 1
			
			# # removed simulated packets loss
			# ack(pkt.seqno)
			# print("ACK ", pkt.seqno)
			
			if(randint(1,10) > 10*plp):
				ack(pkt.seqno)
				f.write(pkt.data)
				print("ACK ", pkt.seqno)
			else:
				expected_seqno -= 1
				print("ACK wasn't sent ", pkt.seqno)
			
			if(pkt.length == 0):
				break
		except socket.timeout:
			print("Timed out!")
	f.close()
	print('Successfully get the file')


def initialize_param():
	global UDP_IP,UDP_PORT, CLIENT_PORT, FILE_NAME 

	with open('client.in') as param_file:
		UDP_IP = param_file.readline().rstrip('\n')
		UDP_PORT = int(param_file.readline())
		CLIENT_PORT = int(param_file.readline())
		FILE_NAME = param_file.readline().rstrip('\n')
		
if __name__ == "__main__":
	initialize_param()
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.settimeout(TIMEOUT_VALUE)	#set recv timeout ==> exception socket.timeout
	sock.bind(("127.0.0.1", CLIENT_PORT))
	print("port: ",CLIENT_PORT)
	# request_file("p.MKV")
	# receive_file("a.MKV")

	request_file(FILE_NAME)
	receive_file(FILE_NAME+"copy")
	sock.close()