from collections import defaultdict
from datetime import datetime
import networkx as nx
import pylab as pl
import __init__
import sql.mysql_helper

class pta:
	
	def __init__(self):
		self.G = defaultdict(list)		
		
	def add_edge(self, n1, e1):
		self.G[n1].append(e1)
		
	def show_graph(self, name):
		pl.figure()
		H = nx.DiGraph()
		for key in self.G.keys():
			for e in self.G[key]:
				H.add_edge(key.Lm, e.d.Lm)
		nx.draw(H)
		pl.savefig(name)
