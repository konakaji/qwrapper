import logging

from qwrapper.obs import Hamiltonian
from qwrapper.operator import ControllablePauli

try:
    import cupy as np
except ModuleNotFoundError:
    print("cupy not found. numpy is used.")
    import numpy as np


class HeisenbergModel(Hamiltonian):
    def __init__(self, nqubit, magnetic=0):
        hs = []
        paulis = []
        coeffs1, p1 = self.interactions(nqubit)
        hs.extend(coeffs1)
        paulis.extend(p1)
        if magnetic != 0:
            p2 = self.magnetic(nqubit)
            paulis.extend(p2)
            hs.extend([magnetic for _ in range(nqubit)])
        super().__init__(hs, paulis, nqubit)

    def interactions(self, nqubit):
        coeffs = []
        results = []
        for j in range(nqubit):
            p1 = j
            p2 = (j + 1) % nqubit
            for char in ["X", "Y", "Z"]:
                coeffs.append(1)
                results.append(self.two_pauli(p1, p2, char, nqubit))
        return coeffs, results

    def magnetic(self, nqubit):
        results = []
        for j in range(nqubit):
            for char in ["X"]:
                results.append(self.one_pauli(j, char, nqubit))
        return results

    def one_pauli(self, p1, char, nqubit):
        return self._pauli([p1], char, nqubit)

    def two_pauli(self, p1, p2, char, nqubit):
        return self._pauli([p1, p2], char, nqubit)

    def _pauli(self, ps, char, nqubit):
        ps = set(ps)
        results = []
        for j in range(nqubit):
            if j in ps:
                results.append(char)
            else:
                results.append("I")
        p_string = "".join(results)
        return ControllablePauli(p_string)


def to_matrix_hamiltonian(hamiltonian: Hamiltonian):
    result = None
    count = 0
    for h, o in zip(hamiltonian.hs, hamiltonian._paulis):
        if result is None:
            result = (h + 0j) * o.to_matrix()
        else:
            result += (h + 0j) * o.to_matrix()
        count += 1
    return result + np.diag([hamiltonian._identity] * len(result))


def compute_ground_state(hamiltonian: Hamiltonian):
    value = min(np.linalg.eigh(to_matrix_hamiltonian(hamiltonian))[0])
    if type(value).__name__ == "ndarray":
        return value.item()
    return value
