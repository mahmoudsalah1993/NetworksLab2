import socket
import signal
from packet import packet

UDP_IP = "127.0.0.1"
UDP_PORT = 9000

FILE_NAME = "some_file_name"
TIMEOUT_VALUE = 3


def signal_handler(signum, frame):
	raise Exception("Timed out!")

def request_file():
	while True:
		signal.signal(signal.SIGALRM, signal_handler)
		signal.alarm(TIMEOUT_VALUE)

		try:
			p = packet(0, len(FILE_NAME), 0, FILE_NAME.encode())
		   	sock.sendto(p.toBuffer(), (UDP_IP, UDP_PORT))

			data, addr = sock.recvfrom(1024)


			# check if ACK
			if len(data) == 8:
				signal.alarm(0)
				break

		except Exception, msg:
			print "Timed out!"

	# file name sent

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    request_file()
    