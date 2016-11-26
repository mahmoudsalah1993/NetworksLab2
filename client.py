import socket

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

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.connect(("localhost", 9000))
    data = "some data"
    #send request here
    sock.sendto(data, ("localhost",9000))
    #loop receive	
    #result = sock.recv(1024)
    #print result
    #sock.close()
