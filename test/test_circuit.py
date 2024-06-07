from qwrapper.circuit import init_circuit
import unittest, numpy as np


class TestCircuit(unittest.TestCase):
    def test_state_vector(self):
        qc = init_circuit(4, "qiskit")
        qc.rx(0.2, 1)
        qc.ry(0.5, 2)
        qc.cnot(1, 3)
        qc.ry(0.5, 3)

        qc2 = init_circuit(4, "qulacs")
        qc2.rx(0.2, 1)
        qc2.ry(0.5, 2)
        qc2.cnot(1, 3)
        qc2.ry(0.5, 3)

        np.testing.assert_array_almost_equal(qc.get_state_vector(), qc2.get_state_vector())

    def test_samples(self):
        qc = init_circuit(4, "qiskit")
        qc.rx(0.2, 1)
        qc.ry(0.5, 2)
        qc.cnot(1, 3)
        qc.ry(0.5, 3)
        print(qc.get_counts(100))

        qc2 = init_circuit(4, "qulacs")
        qc2.rx(0.2, 1)
        qc2.ry(0.5, 2)
        qc2.cnot(1, 3)
        qc2.ry(0.5, 3)
        print(qc2.get_counts(100))
