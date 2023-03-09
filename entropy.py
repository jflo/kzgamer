from bitarray import bitarray

class Entropy:

    def __init__(self):
        self.runningEntropy = bitarray() # will later be divided into 4

    def entropy_add(self, dice) :
        for d in dice:
            rolled = d-3 #keep higher bits from higher rolls
            if rolled < 0:
                continue # skip 1s and 2s being rolled
            print(f"appending {rolled}")
            bit1 = rolled & 1
            bit2 = (rolled >> 1) & 1
            print(f"whos bits are {bit2}{bit1}")
            self.runningEntropy.append(bit2)
            self.runningEntropy.append(bit1)

    def entropy_full(self):
        return len(self.runningEntropy) >= 1024
