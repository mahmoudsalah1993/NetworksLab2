import socket

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
