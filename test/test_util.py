from unittest import TestCase
from math import sqrt
from qwrapper.util import *
from qwrapper.circuit import *


class TestQUtil(TestCase):
    def test_exp_parity(self):
        vector = [0.4, 0, 0, sqrt(1 - 0.4 * 0.4)]
        self.assertAlmostEquals(QUtil.exp_parity(vector, 2), 1)
        vector2 = [0, 0.2, sqrt(1 - 0.2 * 0.2), 0]
        self.assertAlmostEquals(QUtil.exp_parity(vector2, 2), -1)
        vector3 = [0.4 / sqrt(2), 0.2 / sqrt(2), sqrt(1 - 0.2 * 0.2) / sqrt(2), sqrt(1 - 0.4 * 0.4) / sqrt(2)]
        self.assertAlmostEquals(QUtil.exp_parity(vector3, 2), 0)

        qc = QulacsCircuit(3)
        qc.h(0)
        self.assertEquals(QUtil.exp_parity(qc.get_state_vector(), 3, {1, 2}), 0)

    def test_parity(self):
        qc = QulacsCircuit(3)
        qc.h(0)
        for s in qc.get_samples(4):
            self.assertEquals(QUtil.parity(s, {0}), 1)
