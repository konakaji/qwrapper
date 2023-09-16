from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer
from qiskit import execute
from qulacs import QuantumState, QuantumCircuit as QCircuit
from qulacs.gate import H, S, Sdag, X, Y, Z, RX, RY, RZ, CNOT, CZ, merge
from abc import ABC, abstractmethod
from qwrapper.encoder import Encoder
import random, math, numpy as np
import cudaq 


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
    def __init__(self, nqubit):
        self.nqubit = nqubit

    def cx(self, c_index, t_index):
        return self.cnot(c_index, t_index)

    @abstractmethod
    def copy(self):
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
        self.sdag(index)
        self.h(index)

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
    def draw_and_show(self):
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
    def __init__(self, nqubit, gpu=False):
        super().__init__(nqubit)
        self.gpu = gpu
        self.circuit = QCircuit(nqubit)
        self.post_selects = {}
        self._ref_state = None
        #print("Create Qulacs Circuit")

    def copy(self):
        result = QulacsCircuit(self.nqubit)
        result.circuit = self.circuit.copy()
        result.post_selects = self.post_selects.copy()
        result._ref_state = self._ref_state
        return result

    def add_gate(self, gate):
        self.circuit.add_gate(gate)

    def h(self, index):
        #print("h {}".format(index))
        self.circuit.add_H_gate(index)

    def s(self, index):
        #print("s {}".format(index))
        self.circuit.add_S_gate(index)

    def sdag(self, index):
        #print("sdg {}".format(index))
        self.circuit.add_Sdag_gate(index)

    def x(self, index):
        #print("x {}".format(index))
        self.circuit.add_X_gate(index)

    def y(self, index):
        #print("y {}".format(index))
        self.circuit.add_Y_gate(index)

    def z(self, index):
        #print("z {}".format(index))
        self.circuit.add_Z_gate(index)

    def rx(self, theta, index):
        #print("rx({}) {}".format(theta, index))
        self.circuit.add_RX_gate(index, -theta)

    def ry(self, theta, index):
        #print("ry({}) {}".format(theta, index))
        self.circuit.add_RY_gate(index, -theta)

    def rz(self, theta, index):
        #print("rz({}) {}".format(theta, index))
        self.circuit.add_RZ_gate(index, -theta)

    def cnot(self, c_index, t_index):
        #print("cx {} {}".format(c_index, t_index))
        self.circuit.add_CNOT_gate(c_index, t_index)

    def cy(self, c_index, t_index):
        #print("cy {} {}".format(c_index, t_index))
        self.sdag(t_index)
        self.cx(c_index, t_index)
        self.s(t_index)

    def cz(self, c_index, t_index):
        #print("cz {} {}".format(c_index, t_index))
        self.circuit.add_CZ_gate(c_index, t_index)

    def get_q_register(self):
        return None

    def measure_all(self):
        pass

    def barrier(self):
        pass

    def draw(self, output="mpl"):
        pass

    def draw_and_show(self):
        pass

    def get_async_samples(self, nshot) -> Future:
        def listener():
            return self.get_samples(nshot)

        return Future(listener)

    def get_samples(self, nshot):
        state = self._get_ref_state()
        self.circuit.update_quantum_state(state)
        rs = []
        dictionary = {}
        for sample in state.sampling(nshot, seed=random.randint(0, 100000)):
            if sample in dictionary:
                rs.append(dictionary[sample])
            else:
                r = from_bitstring(self._get_bin(sample, self.nqubit))
                dictionary[sample] = r
                rs.append(r)
        return rs

    def get_counts(self, nshot):
        state = self._get_ref_state()
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
        state = self._get_ref_state()
        self.circuit.update_quantum_state(state)
        return state

    def get_state_vector(self):
        state = self._get_ref_state()
        self.circuit.update_quantum_state(state)
        return self.execute_post_selects(state.get_vector(), self.post_selects, self.nqubit)

    def post_select(self, index, value):
        self.post_selects[self.nqubit - index - 1] = value

    def set_ref_state(self, vector):
        if self.gpu:
            from qulacs import QuantumStateGpu
            state = QuantumStateGpu(self.nqubit)
        else:
            state = QuantumState(self.nqubit)
        state.load(vector)
        self._ref_state = state

    def _get_ref_state(self):
        if self._ref_state is not None:
            return self._ref_state.copy()
        if self.gpu:
            from qulacs import QuantumStateGpu
            state = QuantumStateGpu(self.nqubit)
        else:
            state = QuantumState(self.nqubit)
        state.set_zero_state()
        return state

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
        super().__init__(nqubit)
        self._qr = QuantumRegister(nqubit)
        self.qc = QuantumCircuit(self._qr, ClassicalRegister(nqubit))
        self.encoder = Encoder(self.nqubit)
        self.post_selects = {}
        self.draw_mode = False
        self.param_count = 1

    def copy(self):
        result = QiskitCircuit(nqubit=self.nqubit)
        result.qc = self.qc.copy()
        result.encoder = Encoder(self.nqubit)
        result.post_selects = self.post_selects.copy()
        return result

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
        if self.draw_mode:
            self.qc.x(index, label=rf"$R_X(\theta_{{{self.param_count}}})$")
            self.param_count += 1
        else:
            self.qc.rx(theta, index)

    def ry(self, theta, index):
        if self.draw_mode:
            self.qc.x(index, label=rf"$R_Y(\theta_{{{self.param_count}}})$")
            self.param_count += 1
        else:
            self.qc.ry(theta, index)

    def rz(self, theta, index):
        if self.draw_mode:
            self.qc.x(index, label=rf"$R_Z(\theta_{{{self.param_count}}})$")
            self.param_count += 1
        else:
            self.qc.rz(theta, index)

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
        return self.qc.draw(output=output, style={"name": "bw"}, plot_barriers=False)

    def draw_and_show(self):
        self.draw()
        import matplotlib.pyplot as plt
        plt.show()

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
        return np.array(self.execute_post_selects(array, self.post_selects, self.nqubit))

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


class QulacsGate(QWrapper):
    def __init__(self, nqubit):
        super().__init__(nqubit)
        self._gates = []
        self._cache = None

    def apply(self, qc: QulacsCircuit):
        gate = self._compile()
        if gate is not None:
            qc.circuit.add_gate(gate)

    def _compile(self):
        if self._cache is not None:
            return self._cache
        if len(self._gates) == 0:
            return None
        gate = self._gates[0]
        for g in self._gates[1:]:
            gate = merge(gate, g)
        self._cache = gate
        return self._cache

    def h(self, index):
        self._gates.append(H(index))

    def s(self, index):
        self._gates.append(S(index))

    def sdag(self, index):
        self._gates.append(Sdag(index))

    def x(self, index):
        self._gates.append(X(index))

    def y(self, index):
        self._gates.append(Y(index))

    def z(self, index):
        self._gates.append(Z(index))

    def rx(self, theta, index):
        self._gates.append(RX(index, -theta))

    def ry(self, theta, index):
        self._gates.append(RY(index, -theta))

    def rz(self, theta, index):
        self._gates.append(RZ(index, -theta))

    def cnot(self, c_index, t_index):
        self._gates.append(CNOT(c_index, t_index))

    def cy(self, c_index, t_index):
        self.sdag(c_index)
        self.cx(c_index, t_index)
        self.s(c_index)

    def cz(self, c_index, t_index):
        self._gates.append(CZ(c_index, t_index))

    def barrier(self):
        pass

    def get_async_samples(self, nshot):
        raise NotImplementedError('not supported.')

    def measure_all(self):
        raise NotImplementedError('not supported.')

    def get_q_register(self):
        raise NotImplementedError('not supported.')

    def draw(self, output="mpl"):
        pass

    def draw_and_show(self):
        pass

    def get_samples(self, nshot):
        raise NotImplementedError('not supported.')

    def get_counts(self, nshot):
        raise NotImplementedError('not supported.')

    def post_select(self, target, index):
        raise NotImplementedError('not supported.')

    def get_state_vector(self):
        raise NotImplementedError('not supported.')

    @classmethod
    def execute_post_selects(cls, vector, post_selects, n_qubit):
        raise NotImplementedError('not supported.')

    @classmethod
    def execute_post_select(cls, state_vector, i, bit, n_qubit):
        raise NotImplementedError('not supported.')

    def copy(self):
        raise NotImplementedError('not supported.')


class CUDAQuantumCircuit(QWrapper):
    def __init__(self, nqubit):
        super().__init__(nqubit)
        self.gatesToApply = []
        #print("Create CUDAQ Circuit")
        self.numQubits = nqubit 
        self.qarg = cudaq.qvector(nqubit)

    def copy(self):
        raise NotImplementedError('cuda quantum copy - not supported.')

    def h(self, index):
        #print("h {}".format(index))
        self.gatesToApply.append(lambda qarg : cudaq.h(qarg[index]))

    def x(self, index):
        #print("x {}".format(index))
        self.gatesToApply.append(lambda qarg : cudaq.x(qarg[index]))

    def y(self, index):
        #print("y {}".format(index))
        self.gatesToApply.append(lambda qarg : cudaq.y(qarg[index]))

    def z(self, index):
        #print("z {}".format(index))
        self.gatesToApply.append(lambda qarg : cudaq.z(qarg[index]))

    def s(self, index):
        #print("s {}".format(index))
        self.gatesToApply.append(lambda qarg : cudaq.s(qarg[index]))

    def sdag(self, index):
        #print("sdg {}".format(index))
        self.gatesToApply.append(lambda qarg : cudaq.s.adj(qarg[index]))

    def rx(self, theta, index):
        #print("rx({}) {}".format(theta, index))
        self.gatesToApply.append(lambda qarg : cudaq.rx(theta, qarg[index]))

    def ry(self, theta, index):
        #print("ry({}) {}".format(theta, index))
        self.gatesToApply.append(lambda qarg : cudaq.ry(theta, qarg[index]))

    def rz(self, theta, index):
        #print("rz({}) {}".format(theta, index))
        self.gatesToApply.append(lambda qarg : cudaq.rz(theta, qarg[index]))

    def cnot(self, c_index, t_index):
        #print("cx {} {}".format(c_index, t_index))
        self.gatesToApply.append(lambda qarg : cudaq.x.ctrl(qarg[c_index], qarg[t_index]))

    def cy(self, c_index, t_index):
        #print("cy {} {}".format(c_index, t_index))
        self.gatesToApply.append(lambda qarg : cudaq.y.ctrl(qarg[c_index], qarg[t_index]))

    def cz(self, c_index, t_index):
        #print("cz {} {}".format(c_index, t_index))
        self.gatesToApply.append(lambda qarg : cudaq.z.ctrl(qarg[c_index], qarg[t_index]))

    def barrier(self):
        pass
    def draw(self, output="mpl"):
        pass

    def draw_and_show(self):
        pass

    def get_q_register(self):
        raise NotImplementedError('not supported.')
    def post_select(self, index: int, target):
        pass 
    
    def measure_all(self):
        pass
        # self.kernel.mz(self.qubits)


    def get_async_samples(self, nshot) :
        raise NotImplementedError('cuda quantum async_samples - not supported.')

    def get_samples(self, nshot):
        raise NotImplementedError('cuda quantum sanokes - not supported.')


    def get_counts(self, nshot):
        raise NotImplementedError('cuda quantum counts - not supported.')

    def get_state(self):
        raise NotImplementedError('cuda quantum get_state - not supported.')

    def get_state_vector(self):
        raise NotImplementedError('cuda quantum get_state_vector - not supported.')

def init_circuit(nqubit, tool) -> QWrapper:
    if tool == "qulacs":
        return QulacsCircuit(nqubit)
    elif tool == "qulacs-gpu":
        return QulacsCircuit(nqubit, gpu=True)
    elif tool == 'cudaq':
        return CUDAQuantumCircuit(nqubit)
    return QiskitCircuit(nqubit)
