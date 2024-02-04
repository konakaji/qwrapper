import abc
from abc import abstractmethod
from qwrapper.circuit import QWrapper
from qwrapper.util import QUtil
from qulacs import QuantumState, Observable
from qwrapper.circuit import QulacsCircuit, CUDAQuantumCircuit

try:
    import cupy as np
except ModuleNotFoundError:
    print("cupy not found. numpy is used.")
    import numpy as np

try:
    import cudaq
except ModuleNotFoundError:
    print("cudaq not found. numpy is used.")


def build_operator_str(p_string):
    array = []
    for j, c in enumerate(p_string):
        if c == "I":
            continue
        array.append(c)
        array.append(str(j))
    return " ".join(array)


class Pauli:
    X = np.array([[0, 1], [1, 0]])
    Y = np.array([[0, -1j], [1j, 0]])
    Z = np.array([[1, 0], [0, -1]])
    I = np.array([[1, 0], [0, 1]])


class Obs(abc.ABC):
    @abstractmethod
    def get_value(self, qc: QWrapper, nshot):
        pass

    @abstractmethod
    def exact_value(self, qc: QWrapper):
        pass


class PauliObservable(Obs):
    def __init__(self, p_string, sign=1):
        self._p_string = p_string
        self._sign = sign
        self.matrix = None
        self.qulacs_obs = None

    def copy(self):
        return PauliObservable(self._p_string, self._sign)

    @property
    def nqubit(self):
        return len(self.p_string)

    @property
    def p_string(self):
        return self._p_string

    @property
    def sign(self):
        return self._sign

    def get_value(self, qc: QWrapper, nshot):
        if nshot == 0:
            return self.exact_value(qc)
        excludes = self._append(qc)
        result = 0
        for sample in qc.get_samples(nshot):
            result += QUtil.parity(sample, excludes)
        return self.sign * result / nshot

    def exact_value(self, qc: QWrapper):
        if isinstance(qc, QulacsCircuit):
            if self.qulacs_obs is None:
                self.qulacs_obs = self._build_qulacs_obs()
            return self.qulacs_obs.get_expectation_value(qc.get_state())
        if self.matrix is None:
            self.matrix = self.to_matrix()
        vector = qc.get_state_vector()
        return vector.T.conjugate().dot(self.matrix).dot(vector).item(0, 0).real

    def _build_qulacs_obs(self):
        observable = Observable(len(self.p_string))
        observable.add_operator(self.sign, build_operator_str(self.p_string))
        return observable

    def add_circuit(self, qc: QWrapper):
        index = 0
        for c in self.p_string:
            if c == "X":
                qc.x(index)
            elif c == "Y":
                qc.y(index)
            elif c == "Z":
                qc.z(index)
            index += 1

    def add_controlled_circuit(self, control, targets, qc: QWrapper):
        index = 0
        for c in self.p_string:
            target = targets[index]
            if c == "X":
                qc.cx(control, target)
            elif c == "Y":
                qc.cy(control, target)
            elif c == "Z":
                qc.cz(control, target)
            index += 1

    def to_matrix(self):
        m = {"X": Pauli.X, "Y": Pauli.Y,
             "Z": Pauli.Z, "I": Pauli.I}
        matrix = None
        for c in self._p_string:
            if matrix is None:
                matrix = m[c]
            else:
                matrix = np.kron(m[c], matrix)
        return self.sign * matrix

    def _append(self, qc: QWrapper):
        index = 0
        excludes = set()
        for c in self._p_string:
            if c == "X":
                qc.h(index)
            elif c == "Y":
                qc.hsdag(index)
            elif c == "I":
                excludes.add(index)
            index = index + 1
        return excludes

    def __repr__(self) -> str:
        sign_str = '+'
        if self.sign == -1:
            sign_str = '-'
        return f'{sign_str}{self.p_string}'


class Future:
    def __init__(self, do_get):
        self.factor = 1
        self.do_get = do_get

    def get(self):
        return self.factor * self.do_get()

    def __mul__(self, other):
        self.factor = self.factor * other


class Hamiltonian(Obs):
    def __init__(self, hs, paulis: [PauliObservable], nqubit, identity=0):
        self._hs = hs
        self._paulis = paulis
        self._nqubit = nqubit
        self._qulacs_obs = None
        self._matrix = None
        self._identity = identity
        self._cudaq_obs = None

    def save(self, path):
        path = path.replace(" ", "-")
        with open(path, "w") as f:
            for h, pauli in zip(self._hs, self._paulis):
                f.write(f"{h}\t{pauli.p_string}\t{pauli.sign}\n")

    def set_hs(self, hs):
        self._hs = hs

    def get_value(self, qc: QWrapper, nshot, **kwargs):
        if nshot == 0:
            return self.exact_value(qc, **kwargs)
        raise NotImplementedError("get_value for finite shot is not implemented in Hamiltonian class.")

    def exact_value(self, qc: QWrapper, **kwargs):
        if isinstance(qc, CUDAQuantumCircuit):
            if self._cudaq_obs is None:
                self._cudaq_obs = self._build_cudaq_obs()
            for op in qc.gatesToApply:
                op(qc.qarg)

            if 'parallelObserve' in kwargs and kwargs['parallelObserve']:
                print("Async exec on qpu {}".format(kwargs['qpu_id']))
                future = cudaq.observe_async(qc.kernel, self._cudaq_obs, qpu_id=kwargs['qpu_id'])

                def do_get():
                    return future.get().expectation_z() + self._identity

                return Future(do_get)

            return cudaq.observe(qc.kernel, self._cudaq_obs).expectation_z() + self._identity

        if isinstance(qc, QulacsCircuit):
            if self._qulacs_obs is None:
                self._qulacs_obs = self._build_qulacs_obs()
            return self._qulacs_obs.get_expectation_value(qc.get_state()) + self._identity
        if self._matrix is None:
            matrix = np.diag(np.zeros(pow(2, self.nqubit), dtype=np.complex128))
            for h, p in zip(self._hs, self._paulis):
                matrix += h * p.to_matrix()
            self._matrix = matrix
        vector = qc.get_state_vector()
        return vector.T.conjugate().dot(self._matrix).dot(vector).real + self._identity

    @classmethod
    def load(cls, path):
        path = path.replace(" ", "-")
        hs = []
        paulis = []
        n_qubit = None
        with open(path) as f:
            for l in f.readlines():
                h, p_string, sign = l.rstrip().split('\t')
                n_qubit = len(p_string)
                hs.append(float(h))
                paulis.append(PauliObservable(p_string, int(sign)))
        return Hamiltonian(hs, paulis, n_qubit)

    @property
    def nqubit(self):
        return self._nqubit

    @property
    def hs(self):
        return self._hs

    @property
    def paulis(self):
        return self._paulis

    def lam(self):
        result = 0
        for h in self._hs:
            result += h
        return result

    def gen_ancilla_hamiltonian(self, ancilla_obs="X"):
        paulis = []
        for p in self._paulis:
            paulis.append(PauliObservable(p.p_string + ancilla_obs, p.sign))
        return Hamiltonian(self.hs, paulis, self.nqubit + 1)

    def _build_qulacs_obs(self):
        observable = Observable(self.nqubit)
        for h, p in zip(self._hs, self._paulis):
            observable.add_operator(h * p.sign, build_operator_str(p.p_string))
        return observable

    def _build_cudaq_obs(self):
        observable = cudaq.SpinOperator()
        for h, p in zip(self._hs, self._paulis):
            observable += h * p.sign * cudaq.SpinOperator.from_word(p.p_string)
        return observable - cudaq.SpinOperator()

    def __repr__(self) -> str:
        result = ""
        result += ",".join([p.p_string for p in self._paulis])
        result += "\n"
        result += ",".join([str(h) for h in self._hs])
        return result
