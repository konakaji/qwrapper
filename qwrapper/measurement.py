from qwrapper.obs import Hamiltonian
import numpy as np
import random


class MeasurementMethod:
    def __init__(self, hamiltonian: Hamiltonian):
        self.hamiltonian = hamiltonian

    def get_value(self, prepare, ntotal=0, seed=None):
        return np.sum(self.get_values(prepare, ntotal, seed))

    def get_values(self, prepare, ntotal=0, seed=None):
        if seed is not None:
            random.seed(seed)
        if ntotal == 0:
            return self.exact_values(prepare)
        res = []
        nshot = ntotal / len(self.hamiltonian.paulis)
        for h, p in zip(self.hamiltonian.hs, self.hamiltonian.paulis):
            qc = prepare()
            res.append(h * p.get_value(qc, nshot))
        return res

    def exact_value(self, prepare):
        return np.sum(self.exact_values(prepare))

    def exact_values(self, prepare):
        res = []
        for h, p in zip(self.hamiltonian.hs, self.hamiltonian.paulis):
            qc = prepare()
            res.append(h * p.exact_value(qc))
        return res
