import re

class TuringMachine:
	direction = {'R':1, 'r':1, 'S':0, 's':0, 'L':-1, 'l':-1}


	def __init__(self, states:set, start_state:str, terminating_states:set, transforming_funcs_string:str,
	             blank_symbol:set='B', tape_symbols:set=None, input_letters:set=None, tape:str=None):
		self.states = states
		self.start_state = start_state
		self.terminate_states = terminating_states
		self.transform_funcs_raw_string = transforming_funcs_string
		self.blank_symbol = blank_symbol
		self.tape_symbols = tape_symbols
		self.input_letters = input_letters
		self.tape = tape
		self.current_state = start_state

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

	@property
	def tape(self):
		try:
			return self._tape
		except AttributeError:
			self._tape = None
		return self._tape

	@tape.setter
	def tape(self, value: str):
		if not value:
			return
		if self.tape_symbols:
			for letter in value:
				if letter not in self.tape_symbols:
					raise ConstructionError('illegal input tape ' + letter + ' not allowed')
		else:
			tape_symbols = set()
			for letter in value:
				tape_symbols.add(letter)
				self.tape_symbols = tape_symbols
		self._tape = value

	@property
	def tape_symbols(self):
		try:
			return self._tape_symbols
		except AttributeError:
			self._tape_symbols = None
		return self._tape_symbols

	@tape_symbols.setter
	def tape_symbols(self, value):
		self._tape_symbols = value

	@property
	def position(self):
		try:
			return self._position
		except AttributeError:
			self._position = 0
		return self._position

	@position.setter
	def position(self, value: int):
		if value < 0:   # todo 为方便起见，有可能到达-1，指向的字母是 空，这里再做打算
			raise IndexError("position index out of range, position can not be "+str(value))
		self._position = value


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

	@classmethod
	def clean_func_str(cls, funcs_str:str) -> list:
		after_clean = funcs_str.translate(str.maketrans({'\t':'', '\n':'', ' ':''}))   # 删去多余的空白符
		return after_clean.split(';')

	@property
	def transform_funcs(self) -> dict:
		try:
			return self._transform_funcs
		except AttributeError:
			self._transform_funcs = self.generate_transforming_funcs(self.transform_funcs_raw_string)

		return self._transform_funcs

	def _step_forward(self):
		tape = self.tape
		if self.current_state in self.terminate_states:
			raise HaltException
		read_letter = tape[self.position]
		# tuple(starte_state, read_letter) -> tuple(to_state, write_letter, direction)
		next_step = self.transform_funcs[(self.current_state ,read_letter)]
		self.current_state, tape[self.position], direction= next_step
		self.position = self.position + self.__class__.direction[direction]

	def step_forward(self, steps=1) -> list:
		import copy
		process = []
		try:
			for _ in range(steps):
				self._step_forward()
				process.append(copy.deepcopy(self.tape))
		except HaltException:
			pass
		return process


	def run(self) -> bool:
		try:
			for _ in range(1000):
				self._step_forward()
		except HaltException:
			return True

		return False


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




class Tape:
	def __init__(self, string:str):
		self.string = string
		self.length = len(string)




class ConstructionError(Exception):
	pass


class HaltException(Exception):
	pass

import unittest


class MachineTest(unittest.TestCase):
	def setUp(self):
		# 该自动机要求输入带包含3个以上1
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

	def test_match_function(self):  # matching functionality
		result = self.tm.func_pattern.match('f(q0,0)=(q0,0,R)')
		self.assertEqual(result.group('func'), 'f')
		self.assertEqual(result.group('direction'), 'R')
		self.assertEqual(result.group('write_letter'), '0')

	def test_transform_funcs(self):
		funcs = self.tm.transform_funcs
		print(funcs)
		self.assertIsNotNone(funcs)

	def test_tape(self):
		tape = '11001101'
		self.tm.tape = tape
		self.assertEqual(self.tm.tape, tape)
		# illegal tape input
		try:
			self.tm.tape = '121'
		except ConstructionError:
			# 自动机不应该接受 ‘121’这个纸带输入
			self.assertEqual(self.tm.tape, tape)


	def test_turing_machine_functionality(self):
		self.assertTrue(self.tm.run())

