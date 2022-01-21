from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer
from qiskit import execute
from qulacs import QuantumState, QuantumCircuit as QCircuit
from qulacs.gate import Measurement
from abc import ABC, abstractmethod
import random


class Const:
    simulator = Aer.get_backend('qasm_simulator')
    s_simulator = Aer.get_backend('statevector_simulator')


class QWrapper(ABC):
    def cx(self, c_index, t_index):
        return self.cnot(c_index, t_index)

    @abstractmethod
    def h(self, index):
        pass

    @abstractmethod
    def x(self, index):
        pass

    @abstractmethod
    def y(self, index):
        pass

    @abstractmethod
    def z(self, index):
        pass

    @abstractmethod
    def get_q_register(self):
        pass

    @abstractmethod
    def rx(self, theta, index):
        pass

    @abstractmethod
    def ry(self, theta, index):
        pass

    @abstractmethod
    def rz(self, theta, index):
        pass

    @abstractmethod
    def cnot(self, c_index, t_index):
        pass

    @abstractmethod
    def measure_all(self):
        pass

    @abstractmethod
    def barrier(self):
        pass

    @abstractmethod
    def draw(self, output="mpl"):
        pass

    @abstractmethod
    def get_samples(self, nshot):
        pass

    @abstractmethod
    def get_counts(self, nshot):
        pass

    @abstractmethod
    def post_select(self, target, index):
        pass

    @abstractmethod
    def get_state_vector(self):
        pass


class QulacsCircuit(QWrapper):
    def __init__(self, nqubit):
        self.state = QuantumState(nqubit)
        self.state.set_zero_state()
        self.circuit = QCircuit(nqubit)

    def h(self, index):
        self.circuit.add_H_gate(index)

    def x(self, index):
        self.circuit.add_X_gate(index)

    def y(self, index):
        self.circuit.add_Y_gate(index)

    def z(self, index):
        self.circuit.add_Z_gate(index)

    def rx(self, theta, index):
        self.circuit.add_RX_gate(index, theta)

    def ry(self, theta, index):
        self.circuit.add_RY_gate(index, theta)

    def rz(self, theta, index):
        self.circuit.add_RZ_gate(index, theta)

    def cnot(self, c_index, t_index):
        self.circuit.add_CNOT_gate(c_index, t_index)

    def get_q_register(self):
        return None

    def measure_all(self):
        pass

    def barrier(self):
        pass

    def draw(self, output="mpl"):
        pass

    def get_samples(self, nshot):
        rs = []
        for b, v in self.get_counts(nshot).items():
            rs.append([b for _ in range(v)])

    def get_counts(self, nshot):
        self.circuit.update_quantum_state(self.state)
        r = {}
        n_q = self.state.get_qubit_count()
        for sample in self.state.sampling(nshot):
            b = self._get_bin(sample, n_q)
            if b not in r:
                r[b] = 0
            r[b] = r[b] + 1
        return r

    def get_state_vector(self):
        self.circuit.update_quantum_state(self.state)
        return self.state.get_vector()

    def post_select(self, index, value):
        self.circuit.add_gate(Measurement(value, index))

    @classmethod
    def _get_bin(cls, x, n=0):
        """
        Get the binary representation of x.

        Parameters
        ----------
        x : int
        n : int
            Minimum number of digits. If x needs less digits in binary, the rest
            is filled with zeros.

        Returns
        -------
        str
        """
        return format(x, 'b').zfill(n)


class QiskitCircuit(QWrapper):
    def __init__(self, nqubit):
        self.n_qubit = nqubit
        self._qr = QuantumRegister(nqubit)
        self.qc = QuantumCircuit(self._qr)
        self.post_selects = {}

    def h(self, index):
        self.qc.h(index)

    def x(self, index):
        self.qc.x(index)

    def y(self, index):
        self.qc.y(index)

    def z(self, index):
        self.qc.z(index)

    def rx(self, theta, index):
        self.qc.rx(theta, index)

    def ry(self, theta, index):
        self.qc.ry(theta, index)

    def rz(self, theta, index):
        self.qc.rz(theta, index)

    def cnot(self, c_index, t_index):
        self.qc.cnot(c_index, t_index)

    def measure_all(self):
        self.qc.measure_all()

    def post_select(self, target, index: int):
        self.post_selects[index] = str(target)

    def get_q_register(self):
        return self._qr

    def barrier(self):
        self.qc.barrier()

    def draw(self, output="mpl"):
        self.qc.draw(output)

    def get_samples(self, nshot):
        results = []
        while True:
            samples = self._do_get_samples(nshot)
            for sample in samples:
                adopt = False
                for k, v in self.post_selects.items():
                    print(sample)
                    if sample[self.n_qubit - k - 1] == v:
                        adopt = True
                if not adopt:
                    continue
                results.append(sample)
                if len(results) == nshot:
                    return results

    def _do_get_samples(self, nshot):
        self.qc.measure_all()
        job = execute(self.qc, backend=Const.simulator, shots=nshot)
        result = job.result()
        samples = []
        for k, c in result.get_counts().items():
            samples.extend([k for _ in range(c)])
        random.shuffle(samples)
        return samples

    def get_counts(self, nshot):
        if len(self.post_selects) == 0:
            job = execute(self.qc, backend=Const.simulator, shots=nshot)
            return job.result()
        counter = {}
        for sample in self.get_samples(nshot):
            if sample not in counter:
                counter[sample] = 0
            counter[sample] = counter[sample] + 1
        return counter

    def get_state_vector(self):
        job = execute(self.qc, backend=Const.s_simulator)
        return job.result().get_statevector()
