from unittest import TestCase
from qwrapper.circuit import init_circuit
from qwrapper.obs import PauliObservable, Hamiltonian


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

        qc1 = init_circuit(3, "qulacs")
        qc1.h(0)
        qc1.rx(0.7, 1)
        qc1.rx(0.5, 2)

        qc2 = init_circuit(3, "qiskit")
        qc2.h(0)
        qc2.rx(0.7, 1)
        qc2.rx(0.5, 2)

        obs = PauliObservable("IIZ", sign=-1)
        obs2 = PauliObservable("ZZY", sign=1)
        h1 = Hamiltonian([0.5, 0.7], [obs, obs2], 3)

        self.assertAlmostEquals(h1.exact_value(qc1), h1.exact_value(qc2))


class TestHamiltonian(TestCase):
    def test_gen_ancilla_hamiltonian(self):
        obs = PauliObservable("IIZ", sign=-1)
        obs2 = PauliObservable("ZZY", sign=1)
        h = Hamiltonian([0.5, 0.7], [obs, obs2], 3)
        h1 = h.gen_ancilla_hamiltonian("X")
        self.assertEquals(h1.hs[0], 0.5)
        self.assertEquals(h1.hs[1], 0.7)
        self.assertEquals(h1.paulis[0].p_string, "IIZX")
        self.assertEquals(h1.paulis[1].p_string, "ZZYX")
