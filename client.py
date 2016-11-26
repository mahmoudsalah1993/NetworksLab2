import socket
import signal

UDP_IP = "127.0.0.1"
UDP_PORT = 9000

FILE_NAME = "some_file_name"
TIMEOUT_VALUE = 3

class packet:
	def __init__(self, c=0, l=0, s=0, d=[]):
		self.chksum = c
		self.length = l
		self.seqno = s
		self.data = d[:]

	def toBuffer(self):
		res = self.int_to_bytes(self.chksum, 16)
		res += self.int_to_bytes(self.length, 16)
		res += self.int_to_bytes(self.seqno, 32)
		res += self.data
		return res

	def int_to_bytes(self, n, length):
		res = str(n).encode()
		while len(res) < length:
			res = '0'.encode() + res
		return res


def signal_handler(signum, frame):
	raise Exception("Timed out!")

def request_file():
	while True:
		#signal.signal(signal.SIGALRM, signal_handler)
		#signal.alarm(TIMEOUT_VALUE)

		try:
			p = packet(0, len(FILE_NAME), 0, FILE_NAME.encode())
		   	sock.sendto(p.toBuffer(), (UDP_IP, UDP_PORT))

			data, addr = sock.recvfrom(1024)


			    # check if ACK
			if len(data) == 8:
					# turn the alarm off
				break

		except Exception, msg:
			print "Timed out!"

	# file name sent

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    request_file()
    