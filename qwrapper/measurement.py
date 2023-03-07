from qwrapper.obs import Hamiltonian
import random


class MeasurementMethod:
    def __init__(self, hamiltonian: Hamiltonian):
        self.hamiltonian = hamiltonian

    def get_value(self, prepare, ntotal=0, seed=None):
        if seed is not None:
            random.seed(seed)
        if ntotal == 0:
            return self.exact_value(prepare)
        res = 0
        nshot = ntotal / len(self.hamiltonian.paulis)
        for h, p in zip(self.hamiltonian.hs, self.hamiltonian.paulis):
            qc = prepare()
            res += h * p.get_value(qc, nshot)
        return res

    def exact_value(self, prepare):
        res = 0
        for h, p in zip(self.hamiltonian.hs, self.hamiltonian.paulis):
            qc = prepare()
            res += h * p.exact_value(qc)
        return res
