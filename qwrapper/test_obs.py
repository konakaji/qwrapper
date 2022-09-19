from unittest import TestCase
from qwrapper.circuit import init_circuit
from qwrapper.obs import PauliObservable


class TestPauliObservable(TestCase):
    def test_get_value(self):
        qc = init_circuit(3, "qulacs")
        qc.h(0)
        qc.x(1)
        obs = PauliObservable("XZZ")
        self.assertAlmostEqual(-1, obs.get_value(qc, 100))

        qc = init_circuit(3, "qulacs")
        qc.h(0)
        qc.x(1)
        obs = PauliObservable("IZZ")
        self.assertAlmostEqual(-1, obs.get_value(qc, 100))

        qc = init_circuit(3, "qulacs")
        qc.h(0)
        qc.x(1)
        obs = PauliObservable("IIZ")
        self.assertAlmostEqual(1, obs.get_value(qc, 100))
