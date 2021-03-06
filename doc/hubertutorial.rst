.. _hubertutorial:

Huberized lasso tutorial
~~~~~~~~~~~~~~~~~~~~~~~~

The Huberized lasso minimizes the following objective

    .. math::
	H_\delta(Y - X\beta) + \lambda \|\beta\|_1

where :math:`H(\cdot)` is a function applied element-wise,

    .. math::
        H_\delta(r) = \left\{\begin{array}{ll} r^2/2 & \mbox{ if } |r| \leq \delta \\ \delta r - \delta^2/2 & \mbox{ else}\end{array} \right.

To solve this problem using RegReg we begin by loading the necessary numerical libraries

.. ipython::

   import numpy as np

and the RegReg classes necessary for this problem,

.. ipython::

   from regreg.algorithms import FISTA
   from regreg.atoms import l1norm
   from regreg.container import container
   from regreg.smooth import smooth_function, smoothed_seminorm

The l1norm object represents the penalty, the huber_loss class represents the loss function and smooth_function is a container class for combining smooth functions. FISTA is a first-order algorithm and seminorm is a class for combining different seminorm penalties. 

[TODO: Add some real or more interesting data.]

Next, let's generate some example data,

.. ipython::
 
   X = np.random.normal(0,1,500000).reshape((500,1000))
   Y = np.random.randint(0,2,500)

Now we can create the problem object, beginning with the loss function

.. ipython::

   penalty = l1norm(1000,5.)
   loss = smoothed_seminorm(l1norm.affine(X, -Y), epsilon=1.)

The penalty contains the regularization parameter that can be easily accessed and changed,

.. ipython::

   penalty.l 

Now we can create the final problem object

.. ipython::

   problem = container(loss, penalty)

Next, we can select our algorithm of choice and use it solve the problem,

.. ipython::

   solver = FISTA(problem.problem())
   obj_vals = solver.fit(max_its=200, tol=1e-6)
   solution = solver.problem.coefs

Here max_its represents primal iterations, and tol is the primal tolerance. 

.. ipython::

   obj_vals




