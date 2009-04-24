class is_not(ArgumentMatcher):
	def __init__(self, matcher):
		self.matcher = matcher
		
	def matches(self, arg):
		return not self.matcher.matches(arg)
	
	def __str__(self):
		return "is not %s" % (self.matcher,)

#alias
does_not = is_not

class are_not(ArgumentListMatcher):
	def __init__(self, matcher):
		self.matcher = matcher
		
	def matches(self, *args, **kwargs):
		return not self.matcher.matches(*args, **kwargs)
	
	def __str__(self):
		return "are not %s" % (self.matcher,)


