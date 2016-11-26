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

    def int_to_bytes(self, n, length):
        res = str(n).encode()
        while len(res) < length:
            res = '0'.encode() + res
        return res


def parse_packet(p):
    return packet(int(p[:2]), int(p[2:2 + 2]), int(p[4:4 + 4]), p[8:])
        