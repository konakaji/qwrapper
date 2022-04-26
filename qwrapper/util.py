from qwrapper.encoder import Encoder


class QUtil:
    @classmethod
    def parity(cls, sample):
        r = 1
        for s in sample:
            if s == 1:
                r = r * -1
        return r

    @classmethod
    def exp_parity(cls, state_vector, nqubit):
        encoder = Encoder(nqubit)
        result = 0
        for i, s in enumerate(state_vector):
            parity = cls.parity(encoder.encode(i))
            result = result + parity * pow(abs(s), 2)
        return result
