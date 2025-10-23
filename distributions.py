#from numpy.random import normal, uniform, poisson, geometric, choice
from numpy.random import normal, uniform, poisson

class Distribution:
    def __init__(self):
        pass

    def sample(self):
        pass

class NormalDist(Distribution):
    def __init__(self, mean: float, stdev: float):
        super().__init__()
        self.mean: float  = mean
        self.stdev: float = stdev

    def sample(self) -> float:
        return normal(self.mean, self.stdev)

class UniformDist(Distribution):
    def __init__(self, low: float, high: float):
        super().__init__()
        self.low: float = low
        self.high: float = high

    def sample(self):
        return uniform(self.low, self.high)

class PoissonDist(Distribution):
    def __init__(self, lam: float):
        super().__init__()
        self.lam = lam

    def sample(self):
        return poisson(self.lam)
