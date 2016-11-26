import socket
from packet import packet

UDP_IP = "127.0.0.1"
UDP_PORT = 9000

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
		
while True:
	p, addr = sock.recvfrom(1024)
	print "received message:", p