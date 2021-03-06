.. _mixedtutorial:

Mixing seminorms tutorial
~~~~~~~~~~~~~~~~~~~~~~~~~

This tutorial illustrates how to use RegReg to solve problems that have seminorms in both the objective and the contraint. We illustrate with an example:

.. math::

       \frac{1}{2}||y - \beta||^{2}_{2} + \lambda \|\beta\|_1 \text{ subject to} \  ||D\beta||_{1} \leq \delta   

with

.. math::

       D = \left(\begin{array}{rrrrrr} -1 & 1 & 0 & 0 & \cdots & 0 \\ 0 & -1 & 1 & 0 & \cdots & 0 \\ &&&&\cdots &\\ 0 &0&0&\cdots & -1 & 1 \end{array}\right)

To solve this problem using RegReg we begin by loading the necessary numerical libraries

.. ipython::

   import numpy as np
   import pylab	
   from scipy import sparse
   from regreg.algorithms import FISTA
   from regreg.atoms import l1norm
   from regreg.container import container
   from regreg.smooth import l2normsq

The l1norm class is used to represent the :math:`\ell_1` norm, the signal_approximator class represents the loss function and smooth_function is a container class for combining smooth functions. FISTA is a first-order algorithm and container is a class for combining different seminorm penalties. 

Next, let's generate an example signal, and solve the Lagrange form of the problem

.. ipython::
 
   Y = np.random.standard_normal(500); Y[100:150] += 7; Y[250:300] += 14
   loss = l2normsq.shift(-Y, l=0.5)

   sparsity = l1norm(len(Y), 1.4)
   # TODO should make a module to compute typical Ds
   D = sparse.csr_matrix((np.identity(500) + np.diag([-1]*499,k=1))[:-1])
   fused = l1norm.linear(D, 25.5)
   problem = container(loss, sparsity, fused)
   
   solver = FISTA(problem.problem())
   solver.fit(max_its=100, tol=1e-10)
   solution = solver.problem.coefs

We will now solve this problem in constraint form, using the 
achieved  value :math:`\delta = \|D\widehat{\beta}\|_1.
By default, the container class will try to solve this problem with the two-loop strategy.

.. ipython::

   delta = np.fabs(D * solution).sum()
   sparsity = l1norm(len(Y), 1.4)
   fused_constraint = l1norm.linear(D, delta)
   fused_constraint.constraint = True   
   constrained_problem = container(loss, fused_constraint, sparsity)
   constrained_solver = FISTA(constrained_problem.problem())
   constrained_solver.problem.L = 1.01
   vals = constrained_solver.fit(max_its=10, tol=1e-06, backtrack=False, monotonicity_restart=False)
   constrained_solution = constrained_solver.problem.coefs


We can also solve this using the conjugate function :math:`\mathcal{L}_\epsilon^*`

.. ipython::

   loss = l2normsq.shift(-Y, l=0.5)
   true_conjugate = l2normsq.shift(Y, l=0.5)
   problem = container(loss, fused_constraint, sparsity)
   solver = FISTA(problem.conjugate_problem(true_conjugate))
   solver.fit(max_its=200, tol=1e-08)
   conjugate_coefs = problem.conjugate_primal_from_dual(solver.problem.coefs)

Let's also solve this with the generic constraint class, which is called by default when conjugate_problem is called without an argument

.. ipython::

   loss = l2normsq.shift(-Y, l=0.5)
   problem = container(loss, fused_constraint, sparsity)
   solver = FISTA(problem.conjugate_problem())
   solver.fit(max_its=200, tol=1e-08)
   conjugate_coefs_gen = problem.conjugate_primal_from_dual(solver.problem.coefs)


   print np.linalg.norm(solution - constrained_solution) / np.linalg.norm(solution)
   print np.linalg.norm(solution - conjugate_coefs_gen) / np.linalg.norm(solution)
   print np.linalg.norm(conjugate_coefs - conjugate_coefs_gen) / np.linalg.norm(conjugate_coefs)


.. plot::

   import numpy as np
   import pylab	
   from scipy import sparse

   from regreg.algorithms import FISTA
   from regreg.atoms import l1norm
   from regreg.container import container
   from regreg.smooth import l2normsq
 
   Y = np.random.standard_normal(500); Y[100:150] += 7; Y[250:300] += 14
   loss = l2normsq.shift(-Y, l=0.5)

   sparsity = l1norm(len(Y), 1.4)
   # TODO should make a module to compute typical Ds
   D = sparse.csr_matrix((np.identity(500) + np.diag([-1]*499,k=1))[:-1])
   fused = l1norm.linear(D, 25.5)
   problem = container(loss, sparsity, fused)
   
   solver = FISTA(problem.problem())
   solver.fit(max_its=100, tol=1e-10)
   solution = solver.problem.coefs

   delta = np.fabs(D * solution).sum()
   sparsity = l1norm(len(Y), 1.4)
   fused_constraint = l1norm.linear(D, delta)
   fused_constraint.constraint = True   
   constrained_problem = container(loss, fused_constraint, sparsity)
   constrained_solver = FISTA(constrained_problem.problem())
   constrained_solver.problem.L = 1.01
   vals = constrained_solver.fit(max_its=10, tol=1e-06, backtrack=False, monotonicity_restart=False)
   constrained_solution = constrained_solver.problem.coefs


   loss = l2normsq.shift(-Y, l=0.5)
   true_conjugate = l2normsq.shift(Y, l=0.5)
   problem = container(loss, fused_constraint, sparsity)
   solver = FISTA(problem.conjugate_problem(true_conjugate))
   solver.fit(max_its=200, tol=1e-08)
   conjugate_coefs = problem.conjugate_primal_from_dual(solver.problem.coefs)


   loss = l2normsq.shift(-Y, l=0.5)
   problem = container(loss, fused_constraint, sparsity)
   solver = FISTA(problem.conjugate_problem())
   solver.fit(max_its=200, tol=1e-08)
   conjugate_coefs_gen = problem.conjugate_primal_from_dual(solver.problem.coefs)


   pylab.scatter(np.arange(Y.shape[0]), Y)

   pylab.plot(solution, c='y', linewidth=7)	
   pylab.plot(constrained_solution, c='r', linewidth=5)
   pylab.plot(conjugate_coefs, c='black', linewidth=3)	
   pylab.plot(conjugate_coefs_gen, c='gray', linewidth=1)		
