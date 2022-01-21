from qwrapper.circuit import QulacsCircuit, QiskitCircuit
from time import time


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
    compare()
    # print(benchmark(QulacsCircuit(3), 100), benchmark(QiskitCircuit(3), 100))
