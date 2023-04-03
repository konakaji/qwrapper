from unittest import TestCase
from qwrapper.operator import ControllablePauli


class TestControllablePauli(TestCase):
    def test_from_str(self):
        pauli = ControllablePauli.from_str('+XXZ')
        self.assertEquals(1, pauli.sign)
        self.assertEquals("XXZ", pauli.p_string)

        pauli = ControllablePauli.from_str('-XXZ')
        self.assertEquals(-1, pauli.sign)
        self.assertEquals("XXZ", pauli.p_string)
