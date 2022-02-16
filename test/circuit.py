from qwrapper.circuit import QulacsCircuit, QiskitCircuit
from qulacs import QuantumState, QuantumCircuit
from time import time_ns
import unittest, math


class TestCircuit(unittest.TestCase):
    def test_sample(self):
        st = time_ns()
        qc = QulacsCircuit(3)
        def _state_init():
            state = QuantumState(3)
            state.set_zero_state()
            circuit = QuantumCircuit(3)
            circuit.add_H_gate(0)
            circuit.update_quantum_state(state)
            return state.copy()
        qc.state_init = _state_init
        print(qc.get_state_vector())

        qc = QiskitCircuit(3)
        print(qc.get_state_vector())

    def test_postselect(self):
        qc = QulacsCircuit(3)
        qc.rx(2 * math.pi / 3, 0)
        qc.h(1)
        qc.h(2)
        qc.post_select(2, 0)
        vector = qc.get_state_vector()
        for s in vector:
            print(s)
        print("-----------")
        qc = QiskitCircuit(3)
        qc.rx(2 * math.pi / 3, 0)
        qc.h(1)
        qc.h(2)
        qc.post_select(2, 0)
        vector = qc.get_state_vector()
        for s in vector:
            print(s)


def compare():
    qi = QiskitCircuit(3)
    qu = QulacsCircuit(3)

    qi.rx(0.5, 0)
    qu.rx(0.5, 0)
    qi.rx(0.5, 1)
    qu.rx(0.5, 1)
    qi.rx(0.5, 2)
    qu.rx(0.5, 2)
    # qi.post_select(0, 1)
    # qu.post_select(0, 1)
    r = 0
    for v in qu.get_state_vector():
        r = r + v * v.conjugate()
    print(r)
    f = qi.get_async_samples(100)
    f2 = qu.get_async_samples(100)
    print(f.get())
    print(f2.get())
    print("{}, {}".format(qi.get_counts(1000), qu.get_counts(1000)))


def benchmark(qc, loop):
    st = time()
    for j in range(loop):
        qc.rx(0.5, 0)
        qc.rx(0.5, 1)
        qc.rx(0.5, 2)
        qc.measure_all()
        qc.get_counts(100)
    return time() - st


if __name__ == '__main__':
    unittest.main()
    # compare()
    # print(benchmark(QulacsCircuit(3), 100), benchmark(QiskitCircuit(3), 100))
