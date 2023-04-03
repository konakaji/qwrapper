from qwrapper.circuit import QWrapper
from qwrapper.util import QUtil
import numpy as np


class Pauli:
    X = np.matrix([[0, 1], [1, 0]])
    Y = np.matrix([[0, -1j], [1j, 0]])
    Z = np.matrix([[1, 0], [0, -1]])
    I = np.matrix([[1, 0], [0, 1]])


class PauliObservable:
    def __init__(self, p_string, sign=1):
        self._p_string = p_string
        self._sign = sign
        self.matrix = None

    def copy(self):
        return PauliObservable(self._p_string, self._sign)

    @property
    def p_string(self):
        return self._p_string

    @property
    def sign(self):
        return self._sign

    def get_value(self, qc: QWrapper, nshot):
        if nshot == 0:
            return self.exact_value(qc)
        excludes = self._append(qc)
        result = 0
        for sample in qc.get_samples(nshot):
            result += QUtil.parity(sample, excludes)
        return result / nshot

    def exact_value(self, qc: QWrapper):
        if self.matrix is None:
            self.matrix = self.to_matrix()
        vector = qc.get_state_vector()
        return vector.T.conjugate().dot(self.matrix).dot(vector).item(0, 0).real

    def to_matrix(self):
        m = {"X": Pauli.X, "Y": Pauli.Y,
             "Z": Pauli.Z, "I": Pauli.I}
        matrix = None
        for c in self._p_string:
            if matrix is None:
                matrix = m[c]
            else:
                matrix = np.kron(m[c], matrix)
        return self.sign * matrix

    def _append(self, qc: QWrapper):
        index = 0
        excludes = set()
        for c in self._p_string:
            if c == "X":
                qc.h(index)
            elif c == "Y":
                qc.hsdag(index)
            elif c == "I":
                excludes.add(index)
            index = index + 1
        return excludes

    def __repr__(self) -> str:
        sign_str = '+'
        if self.sign == -1:
            sign_str = '-'
        return f'{sign_str}{self.p_string}'


class Hamiltonian:
    def __init__(self, hs, paulis: [PauliObservable], nqubit):
        self._hs = hs
        self._paulis = paulis
        self._nqubit = nqubit

    def save(self, path):
        path = path.replace(" ", "-")
        with open(path, "w") as f:
            for h, pauli in zip(self._hs, self._paulis):
                f.write(f"{h}\t{pauli.p_string}\t{pauli.sign}\n")

    def set_hs(self, hs):
        self._hs = hs

    @classmethod
    def load(cls, path):
        path = path.replace(" ", "-")
        hs = []
        paulis = []
        n_qubit = None
        with open(path) as f:
            for l in f.readlines():
                h, p_string, sign = l.rstrip().split('\t')
                n_qubit = len(p_string)
                hs.append(float(h))
                paulis.append(PauliObservable(p_string, int(sign)))
        return Hamiltonian(hs, paulis, n_qubit)

    @property
    def nqubit(self):
        return self._nqubit

    @property
    def hs(self):
        return self._hs

    @property
    def paulis(self):
        return self._paulis

    def lam(self):
        result = 0
        for h in self._hs:
            result += h
        return result

    def __repr__(self) -> str:
        result = ""
        result += ",".join([p.p_string for p in self._paulis])
        result += "\n"
        result += ",".join([str(h) for h in self._hs])
        return result
