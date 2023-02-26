from bitarray import bitarray

class Entropy:

    def __init__(self):
        self.runningEntropy = bitarray() # will later be divided into 4

    def entropy_add(self, dice) :
        # d[0] - number rolled
        # d[1] - x position in frame
        # d[2] - y position in frame
        for d in dice:
            rolled = d[0]-3 #keep higher bits from higher rolls
            if rolled < 0:
                next # skip 1s and 2s being rolled
            lowestBits = rolled & 0b11
            self.runningEntropy.append(lowestBits)

    def entropy_full(self):
        return len(self.runningEntropy) >= 1024
