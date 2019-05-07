class node:
	
	def __init__(self, lm, pos, rList):
		self.Lm = lm
		self.Pos = pos
		self.Routes = rList
		
	def to_string(self):
		return '##'+str(self.Lm)+':'+self.Pos
