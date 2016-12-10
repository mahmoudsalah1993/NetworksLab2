import socket
import time
from packet import * 
import multiprocessing
import random
import threading
import sched


TIMEOUT_VALUE = 1
UDP_IP = "127.0.0.1"
UDP_PORT = 9000
MAX_WINDOW_SIZE = 10
RANDOM_SEED = 0.6
SCHEDULING_CONST = 10 ** 8
plp = 0.1

lock = threading.Lock()
# shared between sender and reciever threads 
# SHOULDN'T BE ACCESSED DIRECTLY 
mySched = sched.scheduler(time.time, time.sleep)

# map from seqno of pkt to its event
active_events = {}
# helper functions for the scheduler
def add_job(pkt, addr):
	with lock:
		event = s.enter(TIMEOUT_VALUE, SCHEDULING_CONST - pkt.seqno, send_one_pkt, kwargs={'pkg':pkt, 'addr':addr})
		active_events[pkt.seqno] = event


def remove_job(pkt):
	with lock:
		mySched.cancel(active_events[pkt.seqno])

def send_one_pkt(pkt, addr):
	# this function is mainly added for use by mySched
	s.sendto(pkt.toBuffer(), addr)

def send_pkts(s, addr):
	print('start sending file', file_name, 'to client')
	f = open(file_name, "rb")
	base = 0	
	for i in range(MAX_WINDOW_SIZE):
		f.read(512)
		pkt = packet(0, len(l), base + i, l)
		send_one_pkt(pkt)	
		# add a job to scheduler in case of sending failed
		add_job(pkt, addr)
	mySched.run()
	f.close()

def recieve_ACKS(s):
	


def handle_client(file_name, addr):
	global MAX_WINDOW_SIZE

	#creating new soket for that client
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((UDP_IP, UDP_PORT))
	s.settimeout(TIMEOUT_VALUE)

	# ack for file request
	s.sendto(packet(0, 0, 0, b'').toBuffer(), addr)
	print("ACK", 0)

	sender_thread = threading.Thread(target=send_pkts, args=(s, addr,))
	receiver_thread = threading.Thread(target=recieve_ACKS, args=(s,))

	sender_thread.start()
	receiver_thread.start()

	# wait for sending to finish
	receiver_thread.join()



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