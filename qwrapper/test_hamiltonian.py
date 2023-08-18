from unittest import TestCase
from qwrapper.obs import Hamiltonian, PauliObservable
from qwrapper.hamiltonian import compute_ground_state


class Test(TestCase):
    def test_to_matrix_hamiltonian(self):
        hamiltonian = Hamiltonian([0.4, 0.2], [PauliObservable("XXI"),
                                               PauliObservable("YYZ")], 3)
        ge = compute_ground_state(hamiltonian)
        hamiltonian._identity = 0.4
        ge2 = compute_ground_state(hamiltonian)

        self.assertAlmostEquals(ge + 0.4, ge2)
