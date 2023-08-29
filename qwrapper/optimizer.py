import numpy as np
import torch

class Optimizer(object):
    def __init__(self, device="cpu"):
        self.device = device
        
    def optimize(self, function, init_args):
        pass
    
    def to_device(self, data):
        if self.device == 'gpu':
            return torch.tensor(data).to('cuda')
        return data
    
    @classmethod
    def gradient_num_diff(cls, x_center, f, epsilon, recorder=None):
        grad = np.zeros((len(x_center),), float)
        points = []
        ei = np.zeros((len(x_center),), float)
        for k in range(len(x_center)):
            ei[k] = 1.0
            d = epsilon * ei
            point = x_center + d
            points.append(point)
            ei[k] = 0.0
        base = f(x_center)
        if recorder:
            recorder.record(base)
        for i, point in enumerate(points):
            grad[i] = (f(point) - base) / epsilon
        return grad

    @classmethod
    def wrap_function(cls, function, args):
        def function_wrapper(*wrapper_args):
            return function(*(wrapper_args + args))

        return function_wrapper


class LRScheduler:
    def value(self, iteration):
        return 0


class UnitLRScheduler(LRScheduler):
    def __init__(self, lr):
        self.lr = lr

    def value(self, iteration):
        return self.lr


class TransformingLRScheduler(LRScheduler):
    def __init__(self, lr):
        self.lr = lr
        self.map = {}

    def schedule(self, iter, value):
        self.map[iter] = value

    def value(self, iteration):
        if iteration in self.map:
            self.lr = self.map[iteration]
        return self.lr


class Monitor:
    def monitor(self, t, value):
        pass

    def finalize(self):
        pass


class PrintMonitor(Monitor):
    def monitor(self, t, value):
        print(t, value)


class FileMonitor(Monitor):
    def __init__(self, path):
        self.path = path
        self.values = []

    def monitor(self, t, value):
        self.values.append((t, value))

    def finalize(self):
        with open(self.path, "w") as f:
            for t, value in self.values:
                f.write("{}\t{}\n".format(t, value))


class AdamOptimizer(Optimizer):
    def __init__(self, scheduler=UnitLRScheduler(1e-3), maxiter=10000, tol=1e-10, beta_1=0.9, beta_2=0.99,
                 noise_factor=1e-8,
                 eps=1e-10, monitors=[PrintMonitor()]):
        super(AdamOptimizer, self).__init__()
        self._maxiter = maxiter
        self.scheduler = scheduler
        self.monitors = monitors
        self._tol = tol
        self._beta1 = beta_1
        self._beta2 = beta_2
        self._noise_factor = noise_factor
        self._eps = eps
        self._t = 0
        self._m = np.zeros(1)
        self._v = np.zeros(1)

    def do_optimize(self, gradient_function, init_args, func=None):
        params = np.array(init_args)
        params_new = params
        derivative = gradient_function(params)
        self._m = np.zeros(len(derivative))
        self._v = np.zeros(len(derivative))
        while self._t < self._maxiter:
            if func is not None:
                value = func(params)
                for monitor in self.monitors:
                    monitor.monitor(self._t, value)
            derivative = gradient_function(params)
            self._t += 1
            self._m = self._beta1 * self._m + (1 - self._beta1) * derivative
            self._v = self._beta2 * self._v + (1 - self._beta2) * derivative * derivative
            lr_eff = self.scheduler.value(self._t) * np.sqrt(1 - self._beta2 ** self._t) / (1 - self._beta1 ** self._t)
            params_new = params - lr_eff * self._m.flatten() / (np.sqrt(self._v.flatten()) + self._noise_factor)
            if np.linalg.norm(params - params_new) < self._tol:
                return params_new, self._t
            else:
                params = params_new
        return params_new, self._t

    def optimize(self, function, init_args):
        gradient_function = Optimizer.wrap_function(Optimizer.gradient_num_diff, (function, 0.01))
        params_new, t = self.do_optimize(gradient_function, init_args, function)
        return params_new, function(params_new), t




class AdamOptimizerGPU:
    def __init__(self, scheduler, maxiter=10000, tol=1e-10, beta_1=0.9, beta_2=0.99, noise_factor=1e-8, eps=1e-10,
                 monitors=None, device="cpu"):
        self._maxiter = maxiter
        self.scheduler = scheduler
        self.monitors = monitors if monitors is not None else []
        self._tol = tol
        self._beta1 = beta_1
        self._beta2 = beta_2
        self._noise_factor = noise_factor
        self._eps = eps
        self._t = 0
        self.device = device

    def do_optimize(self, gradient_function, init_args, func=None):
        params = torch.tensor(init_args, dtype=torch.float32).to(self.device)
        params_new = params.clone()

        derivative = torch.tensor(gradient_function(params.cpu().numpy()), dtype=torch.float32).to(self.device)

        self._m = torch.zeros_like(derivative)
        self._v = torch.zeros_like(derivative)

        while self._t < self._maxiter:
            if func is not None:
                value = func(params.cpu().numpy())
                for monitor in self.monitors:
                    monitor.monitor(self._t, value)

            derivative = torch.tensor(gradient_function(params.cpu().numpy()), dtype=torch.float32).to(self.device)

            self._t += 1
            self._m = self._beta1 * self._m + (1 - self._beta1) * derivative
            self._v = self._beta2 * self._v + (1 - self._beta2) * derivative ** 2

            lr_eff = self.scheduler.value(self._t) * torch.sqrt(torch.tensor(1.0).to(self.device) - self._beta2 ** self._t) / (1 - self._beta1 ** self._t)


            params_new = params - lr_eff * self._m / (torch.sqrt(self._v) + self._noise_factor)

            if torch.norm(params - params_new) < self._tol:
                return params_new.cpu().numpy(), self._t
            else:
                params = params_new.clone()

        return params_new.cpu().numpy(), self._t

    def optimize(self, function, init_args):
        def wrapped_function(x):
            return function(torch.tensor(x, dtype=torch.float32).to(self.device).cpu().numpy())

        gradient_function = lambda x: np.array(torch.autograd.grad(wrapped_function(torch.tensor(x, dtype=torch.float32).to(self.device)), torch.tensor(x, dtype=torch.float32).to(self.device), create_graph=True)[0].cpu())

        params_new, t = self.do_optimize(gradient_function, init_args, function)

        return params_new, function(params_new), t