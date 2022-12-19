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
		self.depth = [4, 2, 1, 1]

		x, y, u= sp.symbols("x y u")

		self.u = u
		self.x = x
		self.y = y
		self.previous = []
		
		with open('function.json') as json_file:
			self.data = json.load(json_file)
		print("Pronto para começar")

	def calcule(self, px, target, level, index, depth, out):
		score = 1000
		output = 0
		point = np.squeeze(sp.Matrix(self.data[str(level + 1)][depth].split(', ')).subs([(self.x, px[0]), (self.y, px[1])]))
		
		v = (target - point)
		interval_output = np.array([-1,1], np.float32)
		#print("Voltando para o zero", out)
		if level in range(2,5) and out:
			print("Voltando para o zero")
			v[index] = 0
		dist = (sp.sqrt(v @ v.T)).expand()
		diff = sp.diff(dist)
		
		roots = np.array(sp.solve(diff))
		roots_f = roots[roots <= interval_output[1] and roots >= interval_output[0]]

		#bordas
		b1 = dist.subs(self.u, interval_output[1])
		b2 = dist.subs(self.u, interval_output[0])
		output = interval_output[1] if b2 > b1 else interval_output[0]
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
			out = False
			if(np.abs(position[0] )> 0.9 or np.abs(position[1])> 0.9 or np.abs(target[0] )> 0.7 or np.abs(target[1])> 0.7):
				print('Fora x', position)
				out = True
				
				
			if land == 1:
				score = np.ones(4) * 100
				cs = np.ones(4) * 100
				self.clock = (self.clock + 1) % 2
				for i in range(0, self.depth[int(level-1)]):
					cs[i], score[i] = self.calcule(position, target, int(level-1), self.clock, str(25 * (2**i)), out=out)
				ind = np.argmin(score)
				controlSignal = cs[ind]
				print("Scores", score, ind, controlSignal)
			else:
				controlSignal = sin(self.time)

			if controlSignal == self.store and np.abs(controlSignal) == 1:
				print("Estaguinação", self.previous, received)
				
				e = np.array(self.previous[3:5]) - np.array(received[3:5])
				print('fim')
		else:
			controlSignal = sin(self.time)
		self.time += dt
		self.previous = received
		self.store = controlSignal

		return controlSignal


if __name__=='__main__':

	control = Control()

	server = Server(control)

	server.run()








