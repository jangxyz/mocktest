class ArgumentMatcher(object):
	"The root class for all ArgumentMatchers"
	def matches(self, arg):
		raise RuntimeError("override `matches` to implement a matcher")
	
	def __str__(self):
		return "Argument matcher \"%s\"" % (type(self).__name__,)


class ArgumentListMatcher(object):
	"The root class for all ArgumentListMatchers"
	def matches(self, *args, **kwargs):
		raise RuntimeError("override `matches` to implement a matcher")
	
	def __str__(self):
		return "ArgumentList matcher \"%s\"" % (type(self).__name__,)

