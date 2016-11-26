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
