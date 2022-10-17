from qwrapper.circuit import QWrapper
from qwrapper.util import QUtil
import numpy as np


class Pauli:
    X = np.matrix([[0, 1], [1, 0]])
    Y = np.matrix([[0, -1j], [1j, 0]])
    Z = np.matrix([[1, 0], [0, -1]])
    I = np.matrix([[1, 0], [0, 1]])


class PauliObservable:
    def __init__(self, p_string):
        self.p_string = p_string

    def get_value(self, qc: QWrapper, nshot):
        excludes = self._append(qc)
        result = 0
        for sample in qc.get_samples(nshot):
            result += QUtil.parity(sample, excludes)
        return result / nshot

    def exact_value(self, qc: QWrapper):
        matrix = self.to_matrix()
        vector = qc.get_state_vector()
        return vector.T.conjugate().dot(matrix).dot(vector).item(0, 0).real

    def to_matrix(self):
        m = {"X": Pauli.X, "Y": Pauli.Y,
             "Z": Pauli.Z, "I": Pauli.I}
        matrix = None
        for c in self.p_string:
            if matrix is None:
                matrix = m[c]
            else:
                matrix = np.kron(m[c], matrix)
        return matrix

    def _append(self, qc: QWrapper):
        index = 0
        excludes = set()
        for c in self.p_string:
            if c == "X":
                qc.h(index)
            elif c == "Y":
                qc.hsdag(index)
            elif c == "I":
                excludes.add(index)
            index = index + 1
        return excludes
