import random, math

from qutip import Bloch3d
from qwrapper.circuit import init_circuit


def generate_random_bloch():
    b = initialize()
    x1 = random.uniform(-1.0, 1.0)
    x2 = random.uniform(-math.sqrt(1 - x1 ** 2), math.sqrt(1 - x1 ** 2))
    x3 = random.choice([-math.sqrt(1 - x1 ** 2 - x2 ** 2), math.sqrt(1 - x1 ** 2 - x2 ** 2)])
    b.add_vectors([x1, x2, x3])
    return b


def initialize():
    b = Bloch3d()
    b.xlabel = ['', '']
    b.ylabel = ['', '']
    b.vector_color = ['#000000', 'b', 'y']
    b.sphere_color = '#008000'
    b.sphere_alpha = 0.2
    b.vector_width = 6
    b.font_scale = 0.2
    return b


def generate_base_bloch():
    b = initialize()
    b.add_vectors([0, 0, 1.0])
    return b


def generate_one_circuit(nqubit, n_gates):
    qc = init_circuit(nqubit, "qiskit")
    qc.draw_mode = True
    singles = ['h', 'rx', 'ry', 'rz', 's', 'x', 'y', 'z']
    for j in range(n_gates):
        g = random.choice(singles)
        v = random.uniform(0, 1)
        if v > 1 / 3:
            qubit = random.randint(0, nqubit - 1)
            if g == 'h':
                qc.h(qubit)
            elif g == 'rx':
                qc.rx(0, qubit)
            elif g == 'ry':
                qc.ry(0, qubit)
            elif g == 'rz':
                qc.rz(0, qubit)
            elif g == 's':
                qc.s(qubit)
            elif g == 'x':
                qc.x(qubit)
            elif g == 'y':
                qc.y(qubit)
            elif g == 'z':
                qc.z(qubit)
        else:
            f_qubit = random.randint(0, nqubit - 2)
            s_qubit = random.randint(f_qubit + 1, nqubit - 1)
            qc.cnot(f_qubit, s_qubit)
    return qc


if __name__ == '__main__':
    generate_one_circuit(4, 10).draw_and_show()
