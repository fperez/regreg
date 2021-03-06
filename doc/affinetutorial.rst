.. _affinetutorial:

Adding affine offsets to seminorms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tutorial illustrates how to add
an affine part to the seminorm.
Suppose that instead of shrinking the values in the fused LASSO (:ref:`fusedapproxtutorial`_) to 0,
we want to shrink them all towards a given vector :math:`\alpha`

This can be achieved formally  sparse fused lasso minimizes the objective

    .. math::
       \frac{1}{2}||y - \beta||^{2}_{2} + \lambda_{1}||D\beta||_{1} + \lambda_2 \|\beta-\alpha\|_1

    with

    .. math::
       D = \left(\begin{array}{rrrrrr} -1 & 1 & 0 & 0 & \cdots & 0 \\ 0 & -1 & 1 & 0 & \cdots & 0 \\ &&&&\cdots &\\ 0 &0&0&\cdots & -1 & 1 \end{array}\right)

Everything is roughly the same as in the fused LASSO, we just need
to change the second seminorm to have this affine offset.

.. ipython::

   import numpy as np
   import pylab	
   from scipy import sparse

   from regreg.algorithms import FISTA
   from regreg.atoms import l1norm
   from regreg.seminorm import seminorm
   from regreg.smooth import signal_approximator, smooth_function


Let's generate the same example signal,

.. ipython::
 
   Y = np.random.standard_normal(500); Y[100:150] += 7; Y[250:300] += 14

Now we can create the problem object, beginning with the loss function

.. ipython::

   loss = smooth_function(signal_approximator(Y))
   alpha = np.linspace(0,10,500)
   Y += alpha

   shrink_to_alpha = l1norm.shift(alpha, 3.)

which creates an affine_atom object with :math:`\lambda_2=3`. That is, it creates the penalty

.. math::

   3 \|\beta-\alpha\|_{\ell_1(\mathbb{R}^{500})}

that will be added to a smooth loss function.
Next, we create the fused lasso matrix and the associated l1norm object,

.. ipython::

   D = (np.identity(500) + np.diag([-1]*499,k=1))[:-1]
   D
   D = sparse.csr_matrix(D)
   fused = l1norm.linear(D, 25.5)

Here we first created D, converted it a sparse matrix, and then created an l1norm object with the sparse version of D and :math:`\lambda_1 = 25.5`. We can now combine the two l1norm objects using the seminorm container class

.. ipython::

   penalty = seminorm(shrink_to_alpha, fused)

Finally, we can create the final problem object, and solve it.

.. ipython::

   problem = loss.add_seminorm(penalty)
   penalty.atoms
   penalty.atoms[0].l
   solver = FISTA(problem)
   # This problem seems to get stuck restarting
   _ip.magic("time solver.fit(max_its=200, tol=1e-10, monotonicity_restart=False)")
   solution = solver.problem.coefs

Since this problem is a signal approximator, we can also solve
it using blockwise coordinate descent. This is generally faster
for this problem

.. ipython::

   from regreg.blocks import blockwise
   _ip.magic("time block_soln = blockwise(penalty, Y, max_its=500, tol=1.0e-10, min_its=100)")
   np.linalg.norm(block_soln - solution) / np.linalg.norm(solution)
   problem.obj(block_soln), problem.obj(solution)

We can also try smoothing the penalty then follow up the fit
with a blockwise fit. 

.. ipython::

   from regreg.smooth import smoothed_seminorm
   smoothed=smooth_function(smoothed_seminorm(penalty, epsilon=0.01), loss)
   smoothed_solver=FISTA(smoothed)
   _ip.magic("time smoothed_solver.fit(max_its=200, tol=1e-10)")
   smoothed_soln = smoothed_solver.problem.coefs
   _ip.magic("time smoothed_then_block = blockwise(penalty, Y, initial=smoothed_soln, max_its=500, tol=1.0e-07)")

We can then plot solution to see the result of the regression,

.. plot::

   import numpy as np
   import pylab	
   from scipy import sparse
   from regreg.algorithms import FISTA
   from regreg.atoms import l1norm
   from regreg.seminorm import seminorm
   from regreg.smooth import signal_approximator, smooth_function, smoothed_seminorm
   from regreg.problem import dummy_problem
   from regreg.blocks import blockwise

   Y = np.random.standard_normal(500); Y[100:150] += 7; Y[250:300] += 14
   loss = smooth_function(signal_approximator(Y))
   alpha = np.linspace(0,10,500)
   Y += alpha

   shrink_to_alpha = l1norm.shift(alpha, 3.)

   D = (np.identity(500) + np.diag([-1]*499,k=1))[:-1]
   D
   D = sparse.csr_matrix(D)
   fused = l1norm.linear(D, 25.5)

   penalty = seminorm(shrink_to_alpha, fused)

   problem = loss.add_seminorm(penalty)
   solver = FISTA(problem)
   solver.fit(max_its=200, tol=1.0e-07, monotonicity_restart=False)
   solution = solver.problem.coefs
   pylab.plot(solution, c='g', linewidth=4, label=r'$\hat{Y}$')	
   pylab.plot(alpha, c='black', linewidth=3, label=r'$\alpha$')	
   pylab.scatter(np.arange(Y.shape[0]), Y, color='red', label=r'$Y$')
   soln2 = blockwise(penalty, Y, max_its=500, tol=1.0e-10, min_its=100)
   pylab.plot(soln2, c='purple', linewidth=3, label='blockwise')	
   pylab.legend()

   smoothed=smooth_function(smoothed_seminorm(penalty, epsilon=0.01), loss)
   smoothed_solver=FISTA(smoothed)
   smoothed_solver.fit(max_its=200, tol=1e-10)
   smoothed_soln = smoothed_solver.problem.coefs
   smoothed_then_block = blockwise(penalty, Y, initial=smoothed_soln, max_its=500, tol=1.0e-07)
   pylab.plot(smoothed_then_block, c='gray', linewidth=3, label='smoothed + block')	
   pylab.gca().set_xlim([0,650])
   pylab.legend()
