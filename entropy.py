import os

from bitarray import bitarray

class Entropy:

    def __init__(self, collection_goal):
        self.running_entropy = bitarray()
        self.stop_at = collection_goal
        if os.path.isfile("entropy.hex"):
            print("progress found")
            with open("entropy.hex", "r") as f:
                hex_string = f.read().strip()
            self.running_entropy.frombytes(bytes.fromhex(hex_string))
            print(f"resuming from {len(self.running_entropy)} bits")

    def entropy_add(self, dice) :
        for d in dice:
            rolled = d-1
            bit1 = rolled & 1
            bit2 = (rolled >> 1) & 1
            bit3 = (rolled >> 2) & 1
            self.running_entropy.append(bit2)
            self.running_entropy.append(bit1)
            self.running_entropy.append(bit3)

        with open("entropy.hex", "w") as f:
            f.write(self.to_hex_string())


    def entropy_full(self):
        return len(self.running_entropy) >= self.stop_at

    def to_hex_string(self):
        return self.running_entropy.tobytes().hex()

    def bits_collected(self):
        return len(self.running_entropy)

