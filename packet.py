from __future__ import unicode_literals

class packet:
    # WARNING : the parameter c is not used
    def __init__(self, c=0, l=0, s=0, d=[]):
        self.length = l
        self.seqno = s
        self.data = d[:]
        self.chksum = self.checksum()
        
    def toBuffer(self):
        res = self.int_to_bytes(self.chksum, 2)
        res += self.int_to_bytes(self.length, 2)
        res += self.int_to_bytes(self.seqno, 4)
        res += self.data
        return res

    def int_to_bytes(self, n, byteLength):
       return (n).to_bytes(byteLength, byteorder='big', signed=False)
    

    def checksum(self):
        s = 0
        x = self.data
        if(len(x)%2!=0):
           x += ("\0").encode('utf-8')
        for i in range(0, len(x), 2):
            w = x[i] + (x[i+1] << 8)
            s = carry_around_add(s, w)
        return ~s & 0xffff

def bytes_to_int(myBytes):
    return int.from_bytes(myBytes, byteorder='big', signed=False)

def parse_packet(p):
    return packet(bytes_to_int(p[:2]), bytes_to_int(p[2:2 + 2]), bytes_to_int(p[4:4 + 4]), p[8:])

def carry_around_add(a, b):
        c = a + b
        return (c & 0xffff) + (c >> 16)        