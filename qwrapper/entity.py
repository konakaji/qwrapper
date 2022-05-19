from qwrapper.util import QUtil
from qwrapper.encoder import Encoder


class Basis:
    def __init__(self, nqubit):
        self.nqubit = nqubit
        self.bit_array = [0] * nqubit
        self.encoder = Encoder(nqubit)

    def get(self, q_index):
        return self.bit_array[QUtil.get_value(q_index, self.bit_array)]

    def set(self, q_index, bit):
        self.bit_array[QUtil.get_index(q_index, self.nqubit)] = bit

    def to_num(self):
        return self.encoder.decode(self.bit_array)
