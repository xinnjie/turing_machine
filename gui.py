from flask import Flask, render_template, request, flash, redirect
from wtforms import Form, StringField

from turing_machine import TuringMachine, Tape, TMConstructionError

app = Flask(__name__)
app.secret_key = 'hello'

# 由于这个应用作为一个演示图灵机的工具，并没有并发的需求，所以我在这里使用了指向一个图灵机的全局变量
# tm初始是演示用图灵机，把纸带上的所以0改成1
trans_funcs = '''f(q0, 0) = (q0, 1, R);
				f(q0, 1) = (q0, 1, R);
				f(q0, B) = (q1, B, S);
				'''
states = {'q0', 'q1'}
start_state = 'q0'
termin_states = {'q1'}

tm = TuringMachine('modify all 0 to 1', states, start_state, termin_states, trans_funcs, tape='0010101')

g = 0

@app.route('/')
def hello_world():
	global  g
	g += 1
	return 'Hello World!' + str(g)


@app.route('/tm', methods=['GET', 'POST'])
def tm_gui():
	# todo 目标，表格信息填写与图灵机运行分离，可运行多个图灵机
	form = TMForm(request.form)
	if request.method == 'GET':
		global tm
		tape_html = tape2html(*tm.current_tape_pos)
		tm.step_forward()
		return render_template('tm.html', tape_html=tape_html, form=form)
	if request.method == 'POST':
		description = form.description.data
		states = form.states.data.translate(str.maketrans({'\n':'', '\t':'', ' ':''}))
		states = set(states.split(','))
		try:
			states.remove('')
		except:
			pass
		termin_states = form.terminating_states.data.translate(str.maketrans({'\n':'', '\t':'', ' ':''}))
		termin_states = set(termin_states.split(','))
		try:
			termin_states.remove('')
		except:
			pass
		start_state = form.start_state.data
		trans_funcs = form.trans_funcs.data
		blank_symbol = form.blank_symbol.data
		tape_symbols = form.tape_symbols.data
		# 目前不使用blank_symbol和tape_symbol
		tape = form.tape.data
		app.logger.info("trans_funcs is " + str(trans_funcs) )
		try:
			tm = TuringMachine(description, states, start_state, termin_states, trans_funcs, tape=tape)
		except TMConstructionError as e:
			flash('fail to construct the given turing machine, because: '+ str(e), 'error')
			app.logger.error("trans_funcs may not be legal: " + trans_funcs)
			return redirect('/tm')
		flash('succeed to construct the given turing machine and switch', 'info')
		return redirect('/tm')
	# todo 表格一直显示默认值


def tape2html(tape: Tape, pos: int):
	html_list = []
	i = 0
	for letter in tape.string:
		if i == pos:
			html_list.append('<td class="current_pos">{}</td>'.format(letter))
		else:
			html_list.append('<td>{}</td>'.format(letter))
		i += 1
	return '<table class="tape"> {} </table>'.format(''.join(html_list))


class TMForm(Form):
	description = StringField('Description', default='modify all 1s to 0')
	states = StringField('Allowable States', default='q0, q1')
	terminating_states = StringField('Terminating States', default='q1')
	start_state = StringField('Start State', default='q0')
	trans_funcs = StringField('Transforming Functions',
	                          default='f(q0, 1) = (q0, 0, R); f(q0, 0) = (q0, 0, R); f(q0, B) = (q1, B, S)')
	blank_symbol = StringField('Blank Symbol', default='B')
	tape_symbols = StringField('Tape Symbols', default='0,1')
	# input_letters = StringField('')
	tape = StringField('Tape', default='111010101101101')

if __name__ == '__main__':
	app.run(debug=True)
