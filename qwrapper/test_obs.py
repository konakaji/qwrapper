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

    def test_to_string(self):
        obs = PauliObservable("XZZ", 1)
        self.assertEquals(str(obs), "+XZZ")

        obs = PauliObservable("XZZ", -1)
        self.assertEquals(str(obs), "-XZZ")

    def test_exact_value(self):
        qc = init_circuit(3, "qulacs")
        qc.h(0)
        qc.x(1)
        obs = PauliObservable("IIZ", sign=-1)
        self.assertAlmostEqual(-1, obs.exact_value(qc))
