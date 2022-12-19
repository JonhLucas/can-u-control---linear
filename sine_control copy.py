from math import *
from server_base import Server
import numpy as np
import sympy as sp
from sympy.calculus.util import *
import json 

dt = 0.06;

class Control:

	def __init__(self, verbose = False):

		self.verbose = verbose
		self.time = 0.0
		self.dt = 0.01
		self.clock = 1
		self.store = 0.1
		self.previous_score = 1000
		self.score = 1000

		x, y, u= sp.symbols("x y u")

		self.u = u
		self.x = x
		self.y = y
		self.previous = []
		
		with open('function.json') as json_file:
			self.data = json.load(json_file)
		print("Pronto para começar")

	def calcule(self, px, target, level, index):

		#print('calculo', self.data[str(level + 1)]['25'].split(', '))
		score = 1000
		output = 0
		point = np.squeeze(sp.Matrix(self.data[str(level + 1)]['25'].split(', ')).subs([(self.x, px[0]), (self.y, px[1])]))
		
		v = (target - point)
		if level in range(3,5):
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
		score = b1 if b2 > b1 else b2
		if roots_f.shape[0]:
			aux = dist.subs(self.u, output)
			b3 = dist.subs(self.u, roots_f[0])
			output = roots_f[0] if aux > b3 else output
			score = b3 if aux > b3 else aux
		return output, score

	def step(self, received):

		controlSignal = 0
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
				controlSignal, sco = self.calcule(position, target, int(level-1), self.clock)
				print("My control", controlSignal)
			else:
				controlSignal = sin(self.time)
		else:
			controlSignal = sin(self.time)
		self.time += dt
		self.previous = received
		#print(controlSignal, self.score, type(self.score))
		
		'''print('Score:', self.previous_score, self.score)
		if self.score < self.previous_score:
			self.previous_score = self.score
			print('Trocar')
		else:
			controlSignal = self.store
			print("Manter")'''

		if controlSignal == self.store and np.abs(controlSignal) == 1:
			controlSignal = 0
		self.store = controlSignal

		return controlSignal


if __name__=='__main__':

	control = Control()

	server = Server(control)

	server.run()








