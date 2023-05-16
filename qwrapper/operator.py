from qwrapper.circuit import QWrapper, QulacsCircuit, QulacsGate
from qwrapper.obs import PauliObservable


class Operator:
    def add_circuit(self, qc: QWrapper):
        pass


class PauliTimeEvolution(Operator):
    def __init__(self, pauli: PauliObservable, t, cachable=True):
        self.pauli = pauli
        self.t = t
        self.cache = None
        self.cachable = cachable

    def add_circuit(self, qc: QWrapper):
        if not self.cachable or not isinstance(qc, QulacsCircuit):
            self._do_add_circuit(qc)
        else:
            if self.cache is None:
                qg = QulacsGate(qc.nqubit)
                self._do_add_circuit(qg)
                self.cache = qg
            self.cache.apply(qc)

    def _do_add_circuit(self, qc: QWrapper):
        self._rotate_basis(qc)
        qc.barrier()
        pairs = self._cnot_pairs()
        for pair in pairs:
            qc.cnot(pair[0], pair[1])
        qc.barrier()
        index = self._last_nonidentity_index()
        if index is None:
            # identity
            return
        qc.rz(- 2 * self.pauli.sign * self.t, index)
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


class ControllableOperator(Operator):
    def add_controlled_circuit(self, control, targets, qc: QWrapper):
        pass


class ControllablePauli(PauliObservable, ControllableOperator):
    def add_controlled_circuit(self, control, targets, qc: QWrapper):
        index = 0
        for c in self.p_string:
            target = targets[index]
            if c == "X":
                qc.cx(control, target)
            elif c == "Y":
                qc.cy(control, target)
            elif c == "Z":
                qc.cz(control, target)
            index += 1

    def add_circuit(self, qc: QWrapper):
        index = 0
        for c in self.p_string:
            if c == "X":
                qc.x(index)
            elif c == "Y":
                qc.y(index)
            elif c == "Z":
                qc.z(index)
            index += 1

    @classmethod
    def from_str(cls, str):
        if str[0] == '+':
            sign = 1
        elif str[0] == '-':
            sign = -1
        else:
            raise AttributeError('format is wrong')
        return ControllablePauli(str[1:], sign)
