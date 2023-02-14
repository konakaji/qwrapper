from qwrapper.circuit import QWrapper
from qwrapper.obs import PauliObservable


class Operator:
    def add_circuit(self, qc: QWrapper):
        pass


class PauliTimeEvolution(Operator):
    def __init__(self, pauli: PauliObservable, t):
        self.pauli = pauli
        self.t = t

    def add_circuit(self, qc: QWrapper):
        self._rotate_basis(qc)
        qc.barrier()
        pairs = self._cnot_pairs()
        for pair in pairs:
            qc.cnot(pair[0], pair[1])
        qc.barrier()
        qc.rz(- 2 * self.pauli.sign * self.t, self._last_nonidentity_index())
        qc.barrier()
        pairs.reverse()
        for pair in pairs:
            qc.cnot(pair[0], pair[1])
        qc.barrier()
        self._rotate_basis(qc, inverse=True)

    def _rotate_basis(self, qc: QWrapper, inverse=False):
        index = 0
        for c in self.pauli.p_string:
            if c == "X":
                qc.h(index)
            elif c == "Y":
                if inverse:
                    qc.h(index)
                    qc.s(index)
                else:
                    qc.hsdag(index)
            index += 1

    def _last_nonidentity_index(self):
        index = 0
        result = None
        for c in self.pauli.p_string:
            if c != "I":
                result = index
            index += 1
        return result

    def _cnot_pairs(self):
        results = []
        index = 0
        prev = None
        for c in self.pauli.p_string:
            if c == "I":
                index += 1
                continue
            if prev is not None:
                results.append((prev, index))
            prev = index
            index += 1
        return results
