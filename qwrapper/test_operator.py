from unittest import TestCase
from qwrapper.obs import PauliObservable
from qwrapper.operator import ControllablePauli, PauliTimeEvolution
from qwrapper.circuit import init_circuit


class TestControllablePauli(TestCase):
    def test_from_str(self):
        pauli = ControllablePauli.from_str('+XXZ')
        self.assertEquals(1, pauli.sign)
        self.assertEquals("XXZ", pauli.p_string)

        pauli = ControllablePauli.from_str('-XXZ')
        self.assertEquals(-1, pauli.sign)
        self.assertEquals("XXZ", pauli.p_string)

    def test_time_evolution(self):
        pauli = PauliObservable("XXI", 1)
        evolution = PauliTimeEvolution(pauli, 1)
        qc = init_circuit(3, "qulacs")
        evolution.add_circuit(qc)
        evolution.add_circuit(qc)
        print(pauli.get_value(qc, 10))