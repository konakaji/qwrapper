from unittest import TestCase
from qwrapper.circuit import *
import math


class TestQulacsCircuit(TestCase):
    def test_copy_qulacs(self):
        qc = QulacsCircuit(1)
        qc.h(0)
        qc2 = qc.copy()
        qc2.h(0)

        self.assertAlmostEquals(1 / math.sqrt(2), qc.get_state_vector()[0])
        self.assertAlmostEquals(1, qc2.get_state_vector()[0])

    def test_copy_qiskit(self):
        qc = QiskitCircuit(1)
        qc.h(0)
        qc2 = qc.copy()
        qc2.h(0)

        self.assertAlmostEquals(1 / math.sqrt(2), qc.get_state_vector()[0])
        self.assertAlmostEquals(1, qc2.get_state_vector()[0])

    def test_set_ref_state(self):
        qc = QulacsCircuit(3)
        qc.set_ref_state([1 / math.sqrt(2), 0, 0, 0, 1 / math.sqrt(2), 0, 0, 1 / math.sqrt(2)])
        vector = qc.get_state_vector()
        self.assertAlmostEquals(1 / math.sqrt(2), vector[0])
        self.assertAlmostEquals(1 / math.sqrt(2), vector[4])
        self.assertAlmostEquals(1 / math.sqrt(2), vector[7])
