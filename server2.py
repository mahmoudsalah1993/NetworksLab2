import socket
from packet import packet, parse_packet

UDP_IP = "127.0.0.1"
UDP_PORT = 9000

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
		
while True:
	p, addr = sock.recvfrom(1024)
	print "received packet: ", p
	p = parse_packet(p)
	
	print p.chksum
	print p.length
	print p.seqno
	print p.data
