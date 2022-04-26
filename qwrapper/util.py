from qwrapper.encoder import Encoder


class QUtil:
    @classmethod
    def parity(cls, sample, excludes: set = None):
        if excludes is None:
            excludes = {}
        r = 1
        for j, s in enumerate(sample):
            if j in excludes:
                continue
            if s == 1:
                r = r * -1
        return r

    @classmethod
    def exp_parity(cls, state_vector, nqubit, excludes: set = None):
        if excludes is None:
            excludes = {}
        encoder = Encoder(nqubit)
        result = 0
        for i, s in enumerate(state_vector):
            parity = cls.parity(encoder.encode(i), excludes)
            result = result + parity * pow(abs(s), 2)
        return result
