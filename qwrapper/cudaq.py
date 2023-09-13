import cudaq 
from qwrapper.circuit import QWrapper

class CUDAQuantumCircuit(QWrapper):
    def __init__(self, nqubit):
        super().__init__(nqubit)
        self.gatesToApply = []
        print("Create CUDAQ Circuit")
        self.numQubits = nqubit 

    def copy(self):
        raise NotImplementedError('cuda quantum copy - not supported.')

    def h(self, index):
        self.gatesToApply.append(lambda qarg : cudaq.h(qarg[index]))

    def x(self, index):
        self.gatesToApply.append(lambda qarg : cudaq.x(qarg[index]))

    def y(self, index):
        self.gatesToApply.append(lambda qarg : cudaq.y(qarg[index]))

    def z(self, index):
        self.gatesToApply.append(lambda qarg : cudaq.z(qarg[index]))

    def s(self, index):
        self.gatesToApply.append(lambda qarg : cudaq.s(qarg[index]))

    def sdag(self, index):
        self.gatesToApply.append(lambda qarg : cudaq.s.adj(qarg[index]))

    def rx(self, theta, index):
        self.gatesToApply.append(lambda qarg : cudaq.rx(theta, qarg[index]))

    def ry(self, theta, index):
        self.gatesToApply.append(lambda qarg : cudaq.ry(theta, qarg[index]))

    def rz(self, theta, index):
        self.gatesToApply.append(lambda qarg : cudaq.rz(theta, qarg[index]))

    def cnot(self, c_index, t_index):
        self.gatesToApply.append(lambda qarg : cudaq.x.ctrl(qarg[c_index], qarg[t_index]))

    def cy(self, c_index, t_index):
        self.gatesToApply.append(lambda qarg : cudaq.y.ctrl(qarg[c_index], qarg[t_index]))

    def cz(self, c_index, t_index):
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