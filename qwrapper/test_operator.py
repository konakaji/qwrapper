from unittest import TestCase
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

        # evolution = PauliTimeEvolution(ControllablePauli('XY'), 1)
        # qc1 = init_circuit(2, "qulacs")
        # qc2 = init_circuit(2, "qulacs")
        #
        # evolution2 = PauliTimeEvolution(ControllablePauli('XY'), 1, False)
        #
        # from time import time
        #
        # now = time()
        # for _ in range(10000):
        #     evolution.add_circuit(qc1)
        # print("first", time() - now)
        # now = time()
        # for _ in range(10000):
        #     evolution2.add_circuit(qc2)
        # print("second", time() - now)
        #
        # now = time()
        # print(qc1.get_state_vector())
        # print("exec", time() - now)
        # now = time()
        # print(qc2.get_state_vector())
        # print("exec2", time() - now)