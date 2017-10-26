
class Blend:
	def __init__(self, alpha, value=0.0):
		self.alpha = alpha
		self.value = value

	def update(self, value):
		self.value = self.alpha * value + (1.0 - self.alpha) * self.value

	def get_value(self):
		return self.value