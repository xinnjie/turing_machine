import re

class TuringMachine:
	def __init__(self, states:set, start_state:str, terminating_states:set, transforming_funcs_string:str,
	             blank_symbol:set='B', tape_symbols:set=None, input_letters:set=None):
		self.states = states
		self.start_state = start_state
		self.terminate_states = terminating_states
		self.tranform_funcs_string = transforming_funcs_string
		self.blank_symbol = blank_symbol
		self.tape_symbols = tape_symbols
		self.input_letters = input_letters

		self.func_pattern = re.compile(r"""(?P<func>\w+)
										\(
										(?P<start_state>\w+)
										,
										(?P<read_letter>\w)
										\)
										=
										\(
										(?P<to_state>\w+)
										,
										(?P<write_letter>\w)
										,
										(?P<direction>[RrLlSs])
										\)""", re.VERBOSE)

	def generate_transforming_funcs(self, funcs:str):
		# 去掉空格
		funcs = self.clean_func_str(funcs)
		transform_funcs = {}
		for func_string in funcs:
			res = self.func_pattern.match(func_string)
			if res is None:
				raise ConstructionError('transforming func does not match the right format: ' + repr(func_string))
			argument = (res.group('start_state'), res.group('read_letter'))
			return_value = (res.group('to_state'), res.group('write_letter'), res.group('direction'))
			# 每个状态转移函数形式为  tuple(starte_state, read_letter) -> tuple(to_state, write_letter, direction)
			transform_funcs[argument] = return_value   # todo 做检查
		return transform_funcs

	def clean_func_str(self, funcs_str:str) -> list:
		after_clean = funcs_str.translate(str.maketrans({'\t':'', '\n':'', ' ':''}))   # 删去多余的空白符
		return after_clean.split(';')

	@property
	def transform_funcs(self) -> dict:
		try:
			return self._transform_funcs
		except AttributeError:
			self._transform_funcs = self.generate_transforming_funcs(self.tranform_funcs_string)
			return self._transform_funcs
'''
	@property
	def start_state(self):
		return self._start_state

	@start_state.setter
	def start_start(self, value):
		if value in self.states:
			self._start_state = value
			return
		raise ConstructionError("start state must be in states")

'''








class ConstructionError(Exception):
	pass


import unittest
class MachineTest(unittest.TestCase):
	def setUp(self):
		states = {'q0', 'q1', 'q2', 'q3'}
		ter_states = {'q3'}
		start_state = 'q0'
		trans_funcs = '''f(q0, 0) = (q0, 0, R);
						 f(q0, 1) = (q1, 1, R);
						 f(q1, 0) = (q1, 0, R);
						 f(q1, 1) = (q2, 1, R);
						 f(q2, 0) = (q2, 0, R);
						 f(q2, 1) = (q3, 1, R)'''

		self.tm = TuringMachine(states, start_state, ter_states, trans_funcs)

	def test_match_function(self):
		result = self.tm.func_pattern.match('f(q0,0)=(q0,0,R)')
		print(result.groupdict())
		self.assertIsNotNone(self.tm.func_pattern.match('f(q0,0)=(q0,0,R)'))

	def test_transform_funcs(self):
		funcs = self.tm.transform_funcs
		print(funcs)
		self.assertIsNotNone(funcs)


