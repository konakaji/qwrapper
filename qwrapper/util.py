from qwrapper.encoder import Encoder


class QUtil:
    @classmethod
    def parity(cls, sample, excludes: set = None):
        """
        :param sample: bitarray obtained by get_sample of QWrapper (i-th element corresponds to n_qubit - i - 1-th qubit)
        :param excludes: (qubits indices excluded from the computation of the parity)
        :return parity:
        """
        if excludes is None:
            excludes = {}
        r = 1
        n_qubit = len(sample)
        for q_index in range(n_qubit):
            if q_index in excludes:
                continue
            s = cls.get_value(q_index, sample)
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

    @classmethod
    def get_value(cls, q_index, sample):
        """
        :param q_index:
        :param sample:
        :return the bit value corresponds to q_index:
        """
        return sample[cls.get_index(q_index, len(sample))]

    @classmethod
    def get_index(cls, q_index, nqubit):
        return nqubit - 1 - q_index
