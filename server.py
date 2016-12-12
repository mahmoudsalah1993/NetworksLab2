import socket
import time
from packet import * 
import multiprocessing
import random
import threading
import sched
import os

# NOTE : all socket.settimeout() is commented out

TIMEOUT_VALUE = 1
UDP_IP = "127.0.0.1"
UDP_PORT = 9000
windowSize = 10
RANDOM_SEED = 0.6
SCHEDULING_CONST = 10 ** 8
plp = 0.1
ssthresh = 64

lock = threading.Lock()
base = 1
largest_seqno_sent = 0 # largest seqno sent and received ACK for it
# shared between sender and receiver threads 
# SHOULDN'T BE ACCESSED DIRECTLY 
mySched = sched.scheduler(time.time, time.sleep)

# map from seqno of pkt to its event
active_events = {}
# helper functions for the scheduler
def add_job(s, pkt, addr):
	with lock:
		if pkt.seqno in active_events.keys():
			try:
				mySched.cancel(active_events[pkt.seqno])
			except ValueError:
				pass
			del active_events[pkt.seqno]

		event = mySched.enter(TIMEOUT_VALUE, SCHEDULING_CONST - pkt.seqno, send_one_pkt, kwargs={'socket': s, 'pkt':pkt, 'addr':addr})
		active_events[pkt.seqno] = event


def remove_job(pkt):
	global base, largest_seqno_sent
	with lock:
		try:
			if pkt.seqno in active_events.keys():
				largest_seqno_sent = max(largest_seqno_sent, pkt.seqno)
				mySched.cancel(active_events[pkt.seqno])
				del active_events[pkt.seqno]
				
				while not base in active_events.keys() and base <= largest_seqno_sent:
					base += 1
				print('Updated base to', base)

		except ValueError:
			print('Received ack for', pkt.seqno, 'but it\'s not in queue')
	print('*****active_events', list(active_events.keys()), 'sched queue size', len(mySched.queue))
	return len(list(active_events.keys())) == 0

def send_one_pkt(socket, pkt, addr):
	# this function is mainly added for use by mySched
	socket.sendto(pkt.toBuffer(), addr)
	print(' ==>> sent pkt with seqno:', pkt.seqno)
	add_job(socket, pkt, addr)

def send_pkts(s, addr, file_name):
	global base
	print('start sending file', file_name, 'to client')
	f = open(file_name, "rb")
	next_seq = 1

	while 1:
		# print('begining sending with next_seq', next_seq, 'base', base)
		
		while next_seq < base + windowSize:
			l = f.read(512)
			if not l:
				break
			pkt = packet(0, len(l), next_seq, l)
			send_one_pkt(s, pkt, addr)
			# add a job to scheduler in case of sending failed
			add_job(s, pkt, addr)
			next_seq += 1
		
		mySched.run()
		# check if still there some part of the file not sent
		if f.tell() == os.fstat(f.fileno()).st_size:
			f.close()
			print('sender thread done', file_name, 'to', addr)
			return
		else:
			continue

def receive_ACKS(s, sender_thread):
	global windowSize,ssthresh
	last_ack_received = 0
	while sender_thread.is_alive() or last_ack_received != largest_seqno_sent:
		print('Waiting For ACKS...')
		try:
			data, ack_addr = s.recvfrom(1024)
			ack_pkt = parse_packet(data)

			# check if ACK (removed check for ack_addr for now)
			if (ack_pkt.length == 0 and ack_pkt.chksum == ack_pkt.checksum()):
				last_ack_received = ack_pkt.seqno
				print("Received Ack for: ", ack_pkt.seqno, "from",addr)
				remove_job(ack_pkt)
				if(windowSize<ssthresh):
					windowSize *= 2
				else:
					windowSize+=1
			else:
				print('received incorrect ACK')
		except socket.timeout:
			windowSize=1
			if(ssthresh>1):
				ssthresh/=2
			print('receiving ACKS times out noting received')
			pass
		print("ssthresh is",ssthresh," window size ",windowSize)
			
	print('receiver_thread is done')
	return


def handle_client(file_name, addr):
	global windowSize, largest_seqno_sent

	#creating new soket for that client
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((UDP_IP, UDP_PORT))
	s.settimeout(TIMEOUT_VALUE)

	# ack for file request
	s.sendto(packet(0, 0, 0, b'').toBuffer(), addr)
	print("ACK", 0)

	sender_thread = threading.Thread(target=send_pkts, args=(s, addr, file_name,))
	receiver_thread = threading.Thread(target=receive_ACKS, args=(s, sender_thread))

	sender_thread.start()
	receiver_thread.start()

	# wait for sending to finish and the clients ACK the sent packets
	sender_thread.join()
	receiver_thread.join()

	s.sendto(packet(0, 0, largest_seqno_sent + 1, b'').toBuffer(), addr)

	print('finished handling the client', addr)
	print('length of sched queue', len(mySched.queue))



print("Socket started:")

#Ack received pkt
def ack(seqno, addr):
	ack_pkt = packet(0, 0, seqno, b'')
	sock.sendto(ack_pkt.toBuffer(), addr)

def initialize_param():
	global UDP_PORT, windowSize, RANDOM_SEED, plp,MAX_WINDOW_SIZE,windowSize,ssthresh
	windowSize = 1
	with open('server.in') as param_file:
		UDP_PORT = int(param_file.readline())
		MAX_WINDOW_SIZE = int(param_file.readline())
		RANDOM_SEED = float(param_file.readline())
		plp = float(param_file.readline())
		random.seed(RANDOM_SEED)
		ssthresh = MAX_WINDOW_SIZE/2

if __name__ == "__main__":
	initialize_param()

	print('Set listening port to :', UDP_PORT)
	print('Set windowSize to :', windowSize)
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

			if pkt.seqno == 0 and pkt.chksum == pkt.checksum(): # this is actually a file request
				print("File name: \"",(pkt.data).decode('ascii'), "\"")
				UDP_PORT += 1
				new_process = multiprocessing.Process(target=handle_client, args=((pkt.data).decode('ascii'), addr))
				new_process.daemon = True
				new_process.start()
		except socket.timeout:
			pass
	for process in multiprocessing.active_children():
		process.terminate()
		process.join()
