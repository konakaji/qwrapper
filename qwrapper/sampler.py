from abc import ABC, abstractmethod
import random
import math
import numpy as np
from scipy.stats import rv_discrete


class ImportantSampler(ABC):
    @abstractmethod
    def sample_index(self):
        pass

    def sample_indices(self, count):
        return [self.sample_index() for _ in range(count)]


class FasterImportantSampler(ImportantSampler):
    def __init__(self, coeffs):
        self.indices = [j for j in range(len(coeffs))]
        self.p = coeffs / np.sum(coeffs)

    def sample_index(self):
        return self.sample_indices(1)[0]

    def sample_indices(self, count):
        return rv_discrete(values=(self.indices, self.p)).rvs(size=count)


class DefaultImportantSampler(ImportantSampler):
    def __init__(self, coeffs):
        self.borders = []
        total = 0
        for coeff in coeffs:
            total += coeff
            self.borders.append(total)
        self.total = total

    def sample_index(self):
        v = random.uniform(0, self.total)
        start = 0
        end = len(self.borders) - 1
        if v < self.borders[start]:
            return start
        while start + 1 != end:
            middle = math.floor((start + end) / 2)
            if self.borders[middle] <= v:
                start = middle
            else:
                end = middle
        return end
