from math import *
from server_base import Server
import numpy as np
import sympy as sp
from sympy.calculus.util import *

dt = 0.06;

class Control:

	def __init__(self, verbose = False):

		self.verbose = verbose
		self.time = 0.0
		self.dt = 0.01
		self.clock = 1
		self.store = 0.1
		
		A1 = np.array([[-5.2, 2.5],[-9, -0.8]])
		B1 = np.array([[3.2],[5]])

		A2 = np.array([[0, 5],[-9, -0.9]])
		B2 = np.array([[0],[5]])

		A3 = np.array([[-1.2, 2],[3.6, -0.4]])
		B3 = np.array([[0],[-5]])

		A4 = np.array([[1, -0.4],[1.8, 0.2]])
		B4 = np.array([[0.6],[-5]])

		A =  np.stack((A1, A2, A3, A4), axis=0)
		B =  np.stack((B1, B2, B3, B4), axis=0)

		x, y, u= sp.symbols("x y u")
		cx = (np.array([[x], [y]]))
		l = []
		for i in range(0, 100):
			dx = A @ cx + B * u
			xt = cx + dx * self.dt
			cx = xt
			l.append(cx)
		self.path = np.array([l[25], l[50], l[99]])

		self.u = u
		self.x = x
		self.y = y
		self.previous = []
		print(cx, self.path.shape)

	def calcule(self, px, target, level, index):

		print('calculo', self.path[0, level], type(index))
		output = 0
		point = np.squeeze(sp.Matrix(self.path[0, level]).subs([(self.x, px[0]), (self.y, px[1])]))
		
		v = (target - point)
		v[index] = 0
		dist = (sp.sqrt(v @ v.T)).expand()
		diff = sp.diff(dist)
		interval_output = Interval(-1,1)
		roots = np.array(sp.solve(diff))
		roots_f = roots[roots <= 1 and roots >= -1]

		#bordas
		b1 = dist.subs(self.u, 1)
		b2 = dist.subs(self.u, -1)
		output = 1 if b2 > b1 else -1
		if roots_f.shape[0]:
			aux = dist.subs(self.u, output)
			b3 = dist.subs(self.u, roots_f[0])
			output = roots_f[0] if aux > b3 else output
		return output

	def step(self, received):

		controlSignal = 0
		mean = self.store
		if len(received):
			if received == self.previous:
				print("Retroceder")
				return 0
			print(received)
			land = received[1]
			level = received[2]
			position = received[3:5]
			target = received[5:7]
			if land == 1:
				self.clock = (self.clock + 1) % 2
				controlSignal = self.calcule(position, target, int(level-1), self.clock)
				weight = 1
				print("My control", self.store)
			else:
				controlSignal = sin(self.time)
		else:
			controlSignal = sin(self.time)
		self.time += dt
		self.previous = received
		print(controlSignal, self.store, type(self.store))
		
		if controlSignal == self.store and np.abs(controlSignal) == 1:
			controlSignal = 0
		self.store = controlSignal# * weight + self.store * (1-weight)
		return controlSignal


if __name__=='__main__':

	control = Control()

	server = Server(control)

	server.run()








