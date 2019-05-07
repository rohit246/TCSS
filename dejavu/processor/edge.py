class edge:
	
	def __init__(self, l, g, s, p, dist, d):
		self.l = l
		self.g = g
		self.s = s
		self.p = p
		self.dist = dist
		self.d = d
		
	def update_guard():
		self.g = self.g
		
	def update_probability():
		self.p = self.p
		
	def to_string(self):
		return str(self.g)+':'+str(self.s)+':'+str(self.p)+':'+str(self.dist)
