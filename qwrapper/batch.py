import math
from qwrapper.circuit import QWrapper
from qwrapper.obs import PauliObservable
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor


class BatchExecutor(ABC):
    @abstractmethod
    def get_values(self, qcs: [QWrapper], observable,
                   observables: [PauliObservable], nshot: int = None, nshots: [int] = None):
        pass

    @abstractmethod
    def get_exact_values(self, qcs: [QWrapper], observable: [PauliObservable],
                         observables: [PauliObservable]):
        pass

    @classmethod
    def do_get_values(cls, qcs, observables, nshots):
        results = []
        try:
            for qc, nshot, observable in zip(qcs, nshots, observables):
                results.append(observable.get_value(qc, nshot))
        except e:
            import logging
            logging.error("error {}", e)
        return results

    @classmethod
    def do_get_exact_values(cls, qcs, observables):
        results = []
        for qc, observable in zip(qcs, observables):
            results.append(qc.get_state_vector())
        return results

    @classmethod
    def _get_observables(cls, qcs, observable, observables):
        if observable is not None:
            observables = [observable.copy() for _ in range(len(qcs))]
        return observables

    @classmethod
    def _get_nshots(cls, qcs, nshot, nshots):
        if nshot is not None:
            nshots = [nshot for _ in range(len(qcs))]
        return nshots


class NaiveExecutor(BatchExecutor):
    def get_values(self, qcs: [QWrapper], observable: [PauliObservable] = None,
                   observables: [PauliObservable] = None, nshot: int = None, nshots: [int] = None):
        observables = self._get_observables(qcs, observable, observables)
        nshots = self._get_nshots(qcs, nshot, nshots)
        return self.do_get_values(qcs, observables, nshots)

    def get_exact_values(self, qcs: [QWrapper], observable: [PauliObservable] = None,
                         observables: [PauliObservable] = None):
        observables = self._get_observables(qcs, observable, observables)
        return self.do_get_exact_values(qcs, observables)


class AsyncExecutor(BatchExecutor):
    def __init__(self, n_workers=100, partition=1000):
        self.n_workers = n_workers
        self.partition = partition

    def get_values(self, qcs: [QWrapper], observable=None,
                   observables: [PauliObservable] = None, nshot: int = None, nshots: [int] = None):
        observables = self._get_observables(qcs, observable, observables)
        nshots = self._get_nshots(qcs, nshot, nshots)
        futures = []
        with ThreadPoolExecutor(max_workers=self.n_workers) as e:
            for j in range(math.floor(len(qcs) / self.partition)):
                start = self.partition * j
                end = min(self.partition * (j + 1), len(qcs))
                future = e.submit(self.do_get_values, qcs[start:end], observables[start:end], nshots[start: end])
                futures.append(future)
        results = []
        for future in futures:
            results.extend(future.result())
        return results

    def get_exact_values(self, qcs: [QWrapper], observable: [PauliObservable] = None,
                         observables: [PauliObservable] = None):
        observables = self._get_observables(qcs, observable, observables)
        futures = []
        with ThreadPoolExecutor(max_workers=self.n_workers) as e:
            for j in range(math.floor(len(qcs) / self.partition)):
                start = self.partition * j
                end = min(self.partition * (j + 1), len(qcs))
                future = e.submit(self.do_get_exact_values, qcs[start:end], observables[start:end])
                futures.append(future)
                break
        results = []
        for future in futures:
            results.extend(future.result())
        return results
