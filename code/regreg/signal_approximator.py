import numpy as np

# Local imports

from problems import linmodel

class signal_approximator(linmodel):

    """
    LASSO problem with one penalty parameter
    Minimizes

    .. math::
       \begin{eqnarray}
       ||y - D'u||^{2}_{2} s.t. \|u\|_{\infty} \leq  \lambda_{1}
       \end{eqnarray}

    as a function of u and returns (y - u, u) as output.
    """

    def set_coefficients(self, coefs):
        self.dual = coefs

    def get_coefficients(self):
        return self.dual
    coefficients = property(get_coefficients, set_coefficients)

    def initialize(self, data):
        """
        Generate initial tuple of arguments for update.
        """
        if len(data) == 2:
            self.D = data[0]
            self.Y = data[1]
            self.m, self.n = self.D.shape
        else:
            raise ValueError("Data tuple not as expected")

        if hasattr(self,'initial_coefs'):
            self.set_coefficients(self.initial_coefs)
        else:
            self.set_coefficients(self.default_coefs)

    @property
    def default_penalties(self):
        """
        Default penalty for Lasso: a single
        parameter problem.
        """
        return np.zeros(1, np.dtype([(l, np.float) for l in ['l1']]))

    @property
    def default_coefs(self):
        return np.zeros(self.m)

    def obj(self, u):
        u = np.asarray(u)
        beta = self.Y - np.dot(u, self.D)
        return ((self.Y - beta)**2).sum() / 2. + np.sum(np.fabs(np.dot(self.D, beta))) * self.penalties['l1']

    def grad(self, u):
        u = np.asarray(u)
        return np.dot(self.D, np.dot(u, self.D) - self.Y)

    def proximal(self, z, g, L):
        v = z - g / L
        l1 = self.penalties['l1']
        return np.clip(v, -l1/L, l1/L)

    @property
    def output(self):
        r = np.dot(self.dual, self.D) 
        return self.Y - r, r
