import socket
import time
from packet import * 
import multiprocessing
import random
import sched # for scheduling

TIMEOUT_VALUE = 1
UDP_IP = "127.0.0.1"
UDP_PORT = 9000
MAX_WINDOW_SIZE = 10
RANDOM_SEED = 0.6
plp = 0.1

def send_one_pkt(socket, pkt, addr):
	sent = False
	while not sent:
		try:
			s.sendto(pkt.toBuffer(), addr)
			sent = True
		except socket.timeout:
			sent = False
			print('Timed out')

def handle_client(file_name, addr):
	global MAX_WINDOW_SIZE

	#creating new soket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((UDP_IP, UDP_PORT))
	s.settimeout(TIMEOUT_VALUE)

	# ack for file request
	s.sendto(packet(0, 0, 0, b'').toBuffer(), addr)
	print("ACK", 0)
	
	print('start sending file', file_name, 'to client')
	f = open(file_name, "rb")
	base = 0 # sending window base (refer to lectures)
	# base should be updated on receiving ACKs
	seqno = 0
	mySched = sched.scheduler(time.time, time.sleep)
	# schedule MAX_WINDOW_SIZE packets to send
	for i in range(base, base + MAX_WINDOW_SIZE):
		l = f.read(512)
		pkt = packet(0, len(l), seqno, l)
		mySched.enter(1, 1 + base + MAX_WINDOW_SIZE - i, send_one_pkt, kwargs={'socket' : s, 'pkt' : pkt, 'addr' : addr})
	mySched.run()
		



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
		random.seed(RANDOM_SEED)

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
			pkt = parse_packet(p)
			# print("Chksum: ", p.chksum)
			# print("length: ", p.length)
			# print("seqno: ", p.seqno)
			# print("File name: ", (p.data).decode('ascii'))

			if pkt.seqno == 0 and pkt.chksum==pkt.checksum(): # this is actually a file request
				print("File name: ", (pkt.data).decode('ascii'))
				UDP_PORT += 1
				new_process = multiprocessing.Process(target=handle_client, args=((pkt.data).decode('ascii'), addr))
				new_process.daemon = True
				new_process.start()
		except socket.timeout:
			pass
	for process in multiprocessing.active_children():
		process.terminate()
		process.join()
