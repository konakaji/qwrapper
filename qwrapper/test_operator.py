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
        import time

        pauli = PauliObservable("ZYIIII", 1)
        start = time.time()
        evolution = PauliTimeEvolution(pauli, 0.3, cachable=False)
        qc = init_circuit(6, "qulacs")
        qc.h(0)
        qc.h(1)

        obs = PauliObservable("ZZIIII")
        for _ in range(1000):
            evolution.add_circuit(qc)
        print(obs.get_value(qc, 0))
        print(time.time() - start)

        start = time.time()
        evolution = PauliTimeEvolution(pauli, 0.3, cachable=True)
        qc = init_circuit(6, "qulacs")
        qc.h(0)
        qc.h(1)
        for _ in range(1000):
            evolution.add_circuit(qc)
        print(obs.get_value(qc, 0))
        print(time.time() - start)