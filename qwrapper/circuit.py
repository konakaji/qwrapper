from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer
from qiskit import execute
from qulacs import QuantumState, QuantumCircuit as QCircuit
from abc import ABC, abstractmethod
from qwrapper.encoder import Encoder
import random, math


def from_bitstring(str):
    array = []
    for c in str:
        array.append(int(c))
    return array


class Const:
    simulator = Aer.get_backend('qasm_simulator')
    s_simulator = Aer.get_backend('statevector_simulator')


class Future:
    def __init__(self, listener):
        self.listener = listener

    def get(self):
        return self.listener()


class QWrapper(ABC):
    def cx(self, c_index, t_index):
        return self.cnot(c_index, t_index)

    @abstractmethod
    def gen_cache(self):
        pass

    @abstractmethod
    def cache_available(self):
        pass

    @abstractmethod
    def get_async_samples(self, nshot):
        pass

    @abstractmethod
    def h(self, index):
        pass

    @abstractmethod
    def s(self, index):
        pass

    @abstractmethod
    def sdag(self, index):
        pass

    def hsdag(self, index):
        self.h(index)
        self.sdag(index)

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
    def cy(self, c_index, t_index):
        pass

    @abstractmethod
    def cz(self, c_index, t_index):
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

    @classmethod
    def execute_post_selects(cls, vector, post_selects, n_qubit):
        for index, bit in sorted(post_selects.items(), key=lambda item: item[0], reverse=True):
            vector = cls.execute_post_select(vector, index, bit, n_qubit)
        return vector

    @classmethod
    def execute_post_select(cls, state_vector, i, bit, n_qubit):
        results = []
        encoder = Encoder(n_qubit)
        norm = 0
        for num, amplitude in enumerate(state_vector):
            array = encoder.encode(num)
            if array[i] != int(bit):
                results.append(0)
                continue
            results.append(amplitude)
            norm = norm + amplitude * amplitude.conjugate()
        finals = []
        norm = math.sqrt(abs(norm))
        for r in results:
            finals.append(r / norm)
        return finals


class QulacsCircuit(QWrapper):
    def __init__(self, nqubit):
        self.nqubit = nqubit
        self.circuit = QCircuit(nqubit)
        self.post_selects = {}
        state = QuantumState(self.nqubit)
        state.set_zero_state()
        self.state = state

    def cache_available(self):
        return True

    def gen_cache(self):
        state = self.state.copy()
        self.circuit.update_quantum_state(state)
        re = QulacsCircuit(self.nqubit)
        re.state = state
        return re

    def h(self, index):
        self.circuit.add_H_gate(index)

    def s(self, index):
        self.circuit.add_S_gate(index)

    def sdag(self, index):
        self.circuit.add_Sdag_gate(index)

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

    def cy(self, c_index, t_index):
        self.sdag(t_index)
        self.cx(c_index, t_index)
        self.s(t_index)

    def cz(self, c_index, t_index):
        self.circuit.add_CZ_gate(c_index, t_index)

    def get_q_register(self):
        return None

    def measure_all(self):
        pass

    def barrier(self):
        pass

    def draw(self, output="mpl"):
        pass

    def get_async_samples(self, nshot) -> Future:
        def listener():
            return self.get_samples(nshot)

        return Future(listener)

    def get_samples(self, nshot):
        rs = []
        for b, v in self.get_counts(nshot).items():
            rs.extend([from_bitstring(b) for _ in range(v)])
        random.shuffle(rs)
        return rs

    def get_counts(self, nshot):
        state = self.state.copy()
        self.circuit.update_quantum_state(state)
        r = {}
        n_q = state.get_qubit_count()
        for sample in state.sampling(nshot, seed=random.randint(0, 100000)):
            b = self._get_bin(sample, n_q)
            if b not in r:
                r[b] = 0
            r[b] = r[b] + 1
        return r

    def get_state(self):
        state = self.state.copy()
        self.circuit.update_quantum_state(state)
        return state

    def get_state_vector(self):
        state = self.state.copy()
        self.circuit.update_quantum_state(state)
        return self.execute_post_selects(state.get_vector(), self.post_selects, self.nqubit)

    def post_select(self, index, value):
        self.post_selects[self.nqubit - index - 1] = value

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
        self.nqubit = nqubit
        self._qr = QuantumRegister(nqubit)
        self.qc = QuantumCircuit(self._qr, ClassicalRegister(nqubit))
        self.encoder = Encoder(self.nqubit)
        self.post_selects = {}

    def gen_cache(self):
        raise NotImplementedError("gen cache is not avilable")

    def cache_available(self):
        return False

    def h(self, index):
        self.qc.h(index)

    def x(self, index):
        self.qc.x(index)

    def y(self, index):
        self.qc.y(index)

    def z(self, index):
        self.qc.z(index)

    def s(self, index):
        self.qc.s(index)

    def sdag(self, index):
        self.qc.sdg(index)

    def rx(self, theta, index):
        self.qc.rx(-theta, index)

    def ry(self, theta, index):
        self.qc.ry(-theta, index)

    def rz(self, theta, index):
        self.qc.rz(-theta, index)

    def cnot(self, c_index, t_index):
        self.qc.cnot(c_index, t_index)

    def cy(self, c_index, t_index):
        self.qc.cy(c_index, t_index)

    def cz(self, c_index, t_index):
        self.qc.cz(c_index, t_index)

    def measure_all(self):
        self.qc.measure_all()

    def post_select(self, index: int, target):
        self.post_selects[self.nqubit - index - 1] = str(target)

    def get_q_register(self):
        return self._qr

    def barrier(self):
        self.qc.barrier()

    def draw(self, output="mpl"):
        self.qc.draw(output)

    def get_async_samples(self, nshot):
        if self.post_selects is not None:
            def listener():
                return self.get_samples(nshot)

            return Future(listener)

        def listener():
            job = execute(self.qc, backend=Const.simulator, shots=nshot)
            return self._get_result(job)

        return Future(listener)

    def get_samples(self, nshot):
        results = []
        while True:
            samples = self._do_get_samples(nshot)
            for sample in samples:
                adopt = True
                for k, v in self.post_selects.items():
                    if sample[self.nqubit - k - 1] != v:
                        adopt = False
                if not adopt:
                    continue
                results.append(from_bitstring(sample))
                if len(results) == nshot:
                    return results

    def get_counts(self, nshot):
        counter = {}
        for sample in self.get_samples(nshot):
            sample = "".join([str(v) for v in sample])
            if sample not in counter:
                counter[sample] = 0
            counter[sample] = counter[sample] + 1
        return counter

    def get_state_vector(self):
        job = execute(self.qc, backend=Const.s_simulator)
        vector = job.result().get_statevector()
        array = []
        for v in vector:
            array.append(v)
        return self.execute_post_selects(array, self.post_selects, self.nqubit)

    def _do_get_samples(self, nshot):
        self.qc.measure_all(add_bits=False)
        job = execute(self.qc, backend=Const.simulator, shots=nshot)
        return self._get_result(job)

    def _get_result(self, job):
        result = job.result()
        samples = []
        for k, c in result.get_counts().items():
            samples.extend([k for _ in range(c)])
        random.shuffle(samples)
        return samples
