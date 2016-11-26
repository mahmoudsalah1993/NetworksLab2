import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 9000

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

class packet:
	def __init__(self, c=0, l=0, s=0, d=[]):
		self.chksum = c
		self.length = l
		self.seqno = s
		self.data = d[:]

	def toBuffer():
		res = self.int_to_bytes(chksum, 16)
		res += self.int_to_bytes(length, 16)
		res += self.int_to_bytes(seqno, 32)
		res += self.data
		return res

	def int_to_bytes(n, length):
		res = str(n).encode()
		while len(res) < length:
			res = '0'.encode() + res
		return res
		

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "received message:", data