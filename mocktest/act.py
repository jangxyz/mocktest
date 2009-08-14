
def act_upon(acts, fallback, *a, **k):
	"""
	given a set of possible actions, call the first
	one to be applicable
	(calling fallback if none fit)
	"""
	for act in acts:
		if act.should_act(*a, **k):
			return act.action(*a, **k)
	return fallback()

def always(*a, **k): return True

class Act(object):
	def __init__(self, action, when_):
		self.action = action
		self.should_act = when_
		self.acted_upon = []
	
	def act(self, *a, **k):
		self.acted_upon.append((a,k))
		return self.action(*a, **k)

