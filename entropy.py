from bitarray import bitarray
from bitarray import util

class Entropy:

    def __init__(self):
        self.running_entropy = bitarray()

    def entropy_add(self, dice) :
        for d in dice:
            rolled = d-1
            bit1 = rolled & 1
            bit2 = (rolled >> 1) & 1
            bit3 = (rolled >> 2) & 1
            self.running_entropy.append(bit2)
            self.running_entropy.append(bit1)
            self.running_entropy.append(bit3)

    def entropy_full(self):
        return len(self.running_entropy) >= 1024

    def to_hex_string(self):
        if self.running_entropy % 4 == 0:
            return bitarray.util.ba2hex(self.running_entropy)

    def bits_collected(self):
        return len(self.running_entropy)
