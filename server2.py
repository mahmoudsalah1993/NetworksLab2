import socket
import time
from packet import * 
import multiprocessing
from random import randint

plp = 0.1

def handle_client(file_name, addr):
	#creating new soket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((UDP_IP, UDP_PORT))
	s.settimeout(TIMEOUT_VALUE)

	print('start sending file', file_name, 'to client')
	f = open(file_name, "rb")
	seqno = 0
	l = f.read(512)
	print("Start sending the file: ", addr)
	#Start sending the file
	while (l):
		seqno += 1
		pkt = packet(0, len(l), seqno, l)

		while True:	#send pkt and wait for ACK
			try:
				if(randint(1,10) > 10*plp):
					s.sendto(pkt.toBuffer(), addr)
					print("Pkt sent ", seqno,"to ",addr)
				else:
					print("Pkt wasn't sent ", seqno,"to ",addr)
				data, ack_addr = s.recvfrom(1024)
				ack_pkt = parse_packet(data)
				# check if ACK
				if (ack_pkt.length == 0 and ack_pkt.seqno == seqno and ack_addr == addr):
					print("Received Ack for: ",seqno,"to ",addr)
					break
			except socket.timeout:
				print("Timed out!")
		l = f.read(512)
	print('sending package with data_len = 0 to', addr)
	s.sendto(packet(0, 0, seqno + 1, b'').toBuffer(), addr)
	f.close()
	print("-------File sent---------")




TIMEOUT_VALUE = 3
UDP_IP = "127.0.0.1"
UDP_PORT = 9000
MAX_WINDOW_SIZE = 1000
RANDOM_SEED = 0.6

print("Socket started:")

#Ack received pkt
def ack(seqno, addr):
	ack_pkt = packet(0, 0, seqno, b'')
	sock.sendto(ack_pkt.toBuffer(), addr)

def initialize_param():
	global UDP_PORT, MAX_WINDOW_SIZE, RANDOM_SEED, plp

	with open('server.in') as param_file:
		UDP_PORT = int(param_file.readline())
		MAX_WINDOW_SIZE = int(param_file.readline())
		RANDOM_SEED = float(param_file.readline())
		plp = float(param_file.readline())

if __name__ == "__main__":
	initialize_param()

	print('Set listening port to :', UDP_PORT)
	print('Set MAX_WINDOW_SIZE to :', MAX_WINDOW_SIZE)
	print('Set RANDOM_SEED to :', RANDOM_SEED)
	print('Set probability of packet loss to :', plp)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	sock.settimeout(TIMEOUT_VALUE)


	while True:
		try:
			p, addr = sock.recvfrom(1024)
			print("Main received packet: ", p)
			p = parse_packet(p)
			# print("Chksum: ", p.chksum)
			# print("length: ", p.length)
			# print("seqno: ", p.seqno)
			# print("File name: ", (p.data).decode('ascii'))

			if p.seqno == 0 and p.chksum == p.checksum(): # this is actually a file request
				print("File name: ", (p.data).decode('ascii'))
				UDP_PORT += 1
				ack(UDP_PORT, addr)
				print("ACK", p.seqno)
				new_process = multiprocessing.Process(target=handle_client, args=((p.data).decode('ascii'), addr))
				new_process.daemon = True
				new_process.start()
		except socket.timeout:
			pass
	for process in multiprocessing.active_children():
		process.terminate()
		process.join()
