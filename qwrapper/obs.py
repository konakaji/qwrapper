from qwrapper.circuit import QWrapper
from qwrapper.util import QUtil


class PauliObservable:
    def __init__(self, p_string):
        self.p_string = p_string

    def get_value(self, qc: QWrapper, nshot):
        excludes = self._append(qc)
        result = 0
        for sample in qc.get_samples(nshot):
            result += QUtil.parity(sample, excludes)
        return result/nshot

    def _append(self, qc: QWrapper):
        index = 0
        excludes = set()
        for c in self.p_string:
            if c == "X":
                qc.h(index)
            elif c == "Y":
                qc.hsdag(index)
            elif c == "I":
                excludes.add(index)
            index = index + 1
        return excludes
