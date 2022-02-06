import math


class Encoder:
    def __init__(self, n_qubit):
        self.n_qubit = n_qubit

    """
    ex. when n_qubit = 2
    0 -> 00, 1 -> 01, 2 -> 10, 3 -> 11
    """

    def encode(self, num):
        result = []
        value = num
        for n in range(self.n_qubit):
            div = pow(2, self.n_qubit - 1 - n)
            result.append(math.floor(value / div))
            value = value - div * math.floor(value / div)
        return result

    """
    ex. when n_qubit = 2
    00 -> 0, 01 -> 1, 10 -> 2, 11 -> 3
    """

    def decode(self, bit_array):
        result = 0
        for i, bit in enumerate(bit_array):
            result = result + pow(2, self.n_qubit - 1 - i) * bit
        return result

    def to_bitarray(self, bitstring):
        result = []
        for b in bitstring:
            result.append(int(b))
        return result
