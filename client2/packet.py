from __future__ import unicode_literals

class packet:
    def __init__(self, c=0, l=0, s=0, d=[]):
        self.chksum = c
        self.length = l
        self.seqno = s
        self.data = d[:]

    def toBuffer(self):
        res = self.int_to_bytes(self.chksum, 2)
        res += self.int_to_bytes(self.length, 2)
        res += self.int_to_bytes(self.seqno, 4)
        res += self.data
        return res

    def int_to_bytes(self, n, byteLength):
       return (n).to_bytes(byteLength, byteorder='big', signed=False)

def bytes_to_int(myBytes):
    return int.from_bytes(myBytes, byteorder='big', signed=False)

def parse_packet(p):
    return packet(bytes_to_int(p[:2]), bytes_to_int(p[2:2 + 2]), bytes_to_int(p[4:4 + 4]), p[8:])
        