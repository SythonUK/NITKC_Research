# coding: shift-jis
# hmm.py
# Hidden Markov Model のクラス

import numpy as np
from numpy.random import dirichlet
from copy import deepcopy

np.random.seed(100)

class HMM:
	def __init__(self, num_symbols, num_states=3, max_step=500, Pi=None, A=None, B=None):
		p0 = 1.0 / num_states
		if Pi is None:
			Pi = np.ones(num_states) * p0
		if A is None:
			A = np.ones((num_states, num_states)) * p0
		if B is None:
			B = np.ones((num_symbols, num_states)) / num_symbols
		self.num_symbols = num_symbols
		self.num_states = num_states
		self.max_step = max_step
		self.Pi = Pi
		self.A = A
		self.B = B
	
	# 出力分布の初期化
	def init_emission(self, Obs):
		exists = [False] * self.num_symbols
		for obs in Obs:
			for o in obs:
				exists[o] = True
		no = exists.count(True)
		p = dirichlet([1.0] * no, self.num_states)
		i = 0
		for idx, e in enumerate(exists):
			if e:
				self.B[idx, :] = p[:, i]
				i += 1

	# 期待値ステップ
	def Estep(self, obs):
		T = len(obs)
		n = self.num_states

		alpha = np.zeros((T, n))
		c = np.ones(T)
		alpha[0] = self.Pi * self.B[obs[0]]
		alpha[0] /= alpha[0].sum()
		for t in xrange(1, T):
			a = self.B[obs[t]] * np.dot(alpha[t-1], self.A)
			c[t] = a.sum()
			alpha[t] = a / c[t]

		beta = np.zeros((T, n))
		beta[-1] = 1.0
		for t in xrange(T-2, -1, -1):
			beta[t] = np.dot(beta[t+1] * self.B[obs[t+1]], self.A.T) / c[t+1]

		likelihood = np.log(c).sum()
		gamma = alpha * beta
		xisum = sum(
			np.outer(alpha[t-1], self.B[obs[t]] * beta[t]) / c[t] for t in xrange(1, T)
		) * self.A

		return gamma, xisum, likelihood

	# 推論ステップ
	def infer(self, Obs):
		n = self.num_states
		k = self.num_symbols
		new_Pi = np.zeros(n)
		new_A = np.zeros((n, n))
		new_B = np.zeros((k, n))

		log_LH = 0.0
		for obs in Obs:
			gamma, xi_sum, likelihood = self.Estep(obs)
			log_LH += likelihood
			
			new_Pi += gamma[0]
			new_A += xi_sum
			for o, g_t in zip(obs, gamma):
				new_B[o] += g_t

		self.Pi = new_Pi / new_Pi.sum()
		self.A = new_A / (new_A.sum(1)[:, np.newaxis])
		self.B = new_B / new_B.sum(0)

		return log_LH

	# HMM の学習
	def learning(self, Obs, eps=1e-5):
		prev_LH = -1e10
		self.init_emission(Obs)
		for step in xrange(self.max_step):
			log_LH = self.infer(Obs)
			diff = prev_LH - log_LH
			if abs(diff) < eps: break
			prev_LH = log_LH
