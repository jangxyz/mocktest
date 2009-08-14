"""
SilentMock makes many attempts to hide the fact that it is a mock object.
Attribute accesses, sets and object calls are recorded internally, and can be
inspected passing the silent mock into a MockWrapper object.
"""

from lib.realsetter import RealSetter
from lib.singletonclass import SingletonClass
from callrecord import CallRecord
from mockerror import MockError

DEFAULT = object()
__unittest = True

def raw_mock(name = None, **kwargs):
	"""a silent mock object. use mock_of(silent_mock) to set expectations, etc"""
	if name is not None:
		if not isinstance(name, str):
			raise TypeError("%r is not a string. did you mean to use mock_on(%r)?" % (name, name))
		kwargs['name'] = name
	return SilentMock(**kwargs)

class SilentMock(RealSetter, SingletonClass):
	def __init__(self, **kwargs):
		self._real_set(_mock_dict = {
					'_actions': None,
					'return_value':DEFAULT,
					'name':'unnamed mock',
					'_children':{},
					'_modifiable_children':True,
					'_return_value_provided':False,
					'_should_intercept':True,
					'_proxied': None,
				})
		self._mock_reset()
		self._mock_set(**kwargs)

	def _mock_reset(self):
		resets = {
			'call_list':[],
		}
		for key,val in resets.items():
			self._mock_dict[key] = val
	
	def _mock_set(self, **kwargs):
		for attr, val in kwargs.items():
			if not attr in self._mock_dict:
				raise KeyError, "no such mock attribute: %s" % (attr,)
			self._mock_dict[attr] = val
	
	def _mock_get(self, attr, **kwargs):
		if 'default' in kwargs:
			return self._mock_dict.get(attr, kwargs['default'])
		return self._mock_dict[attr]
	
	def __call__(self, *args, **kwargs):
		retval = None
		acted = [True] # this is an array so we can mutate it in lieu of "nonlocal"
		try:
			def do_proxy(*a, **k):
				proxy = self._mock_get('_proxied')
				if proxy is None:
					# the default action is to return a new anonymous silent mock
					proxy = lambda *a, **k: self._mock_get('return_value')
				else:
					# this is the only branch where we're *NOT* counting ourselves as called
					acted[0] = False
				return proxy(*a, **k)
			retval = act.act_upon(self._mock_get('_actions'), proxy, *args, **kwargs)
		finally:
			if acted[0]:
				self._mock_get('call_list').append(CallRecord(args, kwargs))

		if retval is DEFAULT:
			retval = raw_mock(name="return value for (%s)" % (self._mock_get('name')))
			# note this so that future calls get the same result
			self._mock_set(return_value = retval)
		return retval

	def _mock_fail_if_no_child_allowed(self, name):
		if name not in self._mock_get('_children'):
			if not self._mock_get('_modifiable_children'):
				raise AttributeError, "object (%s) has no attribute '%s'" % (self, name,)

	def _assign_special_method(self, name, val):
		special_method = name.startswith('__') and name.endswith('__')
		if special_method:
			self._ensure_singleton_class()
			setattr(type(self), name, val)

	def __setattr__(self, attr, val):
		self._mock_fail_if_no_child_allowed(attr)
		self._assign_special_method(attr, val)
		self._mock_get('_children')[attr] = val

	def _mock_get_child(self, name, force=False):
		"""
		called by e.g silentmock.child_name
		if "child_name" is not in _mock_dict,
		it will be added and set to a new silent mock
		if (and only if) this mock is not frozen
		"""
		def _new():
			self._mock_get('_children')[name] = raw_mock(name=name)
			return self._mock_get('_children')[name]
		
		if name not in self._mock_get('_children'):
			if not force:
				self._mock_fail_if_no_child_allowed(name)
			child = _new()
		else:
			# child already exists
			child = self._mock_get('_children')[name]
			if child is DEFAULT:
				child = _new()
		self._assign_special_method(name, child)
		return child
	
	def __getattribute__(self, name):
		if name.startswith('__') and name.endswith('__'):
			# Attempt to get special methods directly, without exception
			# handling
			return object.__getattribute__(self, name)
		elif name.startswith('_'):
			try:
				# Attempt to get the attribute, if that fails
				# treat it as a child
				return object.__getattribute__(self, name)
			except AttributeError:
				pass
		return self._mock_get_child(name)
			
	def __str__(self):
		return str(self._mock_get('name'))
	def __name__(self): return str(self)
	
	def __repr__(self):
		return '<raw mock "%s">' % (str(self),)
