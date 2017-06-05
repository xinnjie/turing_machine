from flask import Flask, render_template, request, flash, redirect, url_for
from wtforms import Form, StringField, TextAreaField, validators

from turing_machine import TuringMachine, Tape, TMConstructionError, HaltException, BreakDownException

# app config
app = Flask(__name__)
app.secret_key = 'hello'
ALLOWED_EXTENSIONS = {'txt'}


# 由于这个应用作为一个演示图灵机的工具，并没有并发的需求，所以我在这里使用了指向一个图灵机的全局变量
# tm初始是演示用图灵机，把纸带上的所以0改成1
trans_funcs = 'f(q0, 0) = (q0, 1, R);\n f(q0, 1) = (q0, 1, R);\nf(q0, B) = (q1, B, S);'
states = {'q0', 'q1'}
start_state = 'q0'
termin_states = {'q1'}

tm = TuringMachine('modify all 0 to 1', states, start_state, termin_states, trans_funcs, tape='0010101')


@app.route('/', methods=['GET', 'POST'])
def tm_gui():
	# todo 目标，表格信息填写与图灵机运行分离，可运行多个图灵机
	form = TMForm(request.form)
	if request.method == 'GET':
		global tm
		tape_html = tape2html(*tm.current_tape_pos)
		try:
			tm.step_forward()
		except BreakDownException as e:
			flash(str(e), 'Error')
			return redirect('/')
		try:
			next_trans_func = tm.next_transforming_func
		except HaltException:
			next_trans_func = 'turing machine halted'
			flash('turing machine halted', 'Info')
		except BreakDownException:
			next_trans_func = 'next transforming func not exist'
			flash('next transforming func not exist', 'Error')
		data = {'states': set2str(tm.states), 'terminate_states':set2str(tm.terminate_states) , 'tape_symbols':set2str(tm.tape_symbols)}

		return render_template('tm.html', tape_html=tape_html, form=form, next_trans_func=next_trans_func, current_tm=tm, data=data)
	if request.method == 'POST':
		if 'new_tm' in request.files:
			file = request.files['new_tm']
			# upload empty file
			if file.filename == '':
				flash('the file is empty', 'Error')
				return redirect('/')
			if file and allowed_file(file.filename):
				try:
					description, states, start_state, termin_states, trans_funcs, tape = file.read().decode().splitlines()[0:6]
				except IndexError as e:
					app.logger.error(str(e))
					flash('the uploaded TM do not fit', 'Error')
					return redirect('/')
				except ValueError as e:
					app.logger.error(str(e))
					flash("the file doesn't match the format   "+str(e), 'Error')
					return redirect('/')
		# if there is no file uploaded, then check the form
		else:
			description = form.description.data
			states = form.states.data
			termin_states = form.terminating_states.data
			start_state = form.start_state.data
			trans_funcs = form.trans_funcs.data
			blank_symbol = form.blank_symbol.data
			tape_symbols = form.tape_symbols.data
			tape = form.tape.data

		states = states.translate(str.maketrans({'\n':'', '\t':'', ' ':''}))
		states = set(states.split(','))
		try:
			states.remove('')
		except:
			pass
		termin_states = termin_states.translate(str.maketrans({'\n':'', '\t':'', ' ':''}))
		termin_states = set(termin_states.split(','))
		try:
			termin_states.remove('')
		except:
			pass
		# 目前不使用blank_symbol和tape_symbol
		app.logger.info("trans_funcs is " + trans_funcs )
		try:
			tm = TuringMachine(description, states, start_state, termin_states, trans_funcs, tape=tape)
		except TMConstructionError as e:
			flash('fail to construct the given turing machine, because: '+ str(e), 'error')
			app.logger.error('fail to construct the given tutring machine, because '+str(e))
			return redirect('/')
		flash('succeed to construct the given turing machine and switch', 'info')
		return redirect('/')

@app.route('/run')
def tm_run():
	if not tm.run():
		flash('this machine may not stop(has steped forward 1000 times)', 'Info')
	return redirect('/')



def tape2html(tape: Tape, pos: int):
	html_list = []
	for i in range(max(len(tape.string), pos+1)):
		if i == pos:
			html_list.append('<td class="current_pos">{}</td>'.format(tape[i]))
		else:
			html_list.append('<td>{}</td>'.format(tape[i]))

	# if pos is at the last of the tape string add extra blank symbol to it
	# if pos >= len(tape.string)-1:
	# 	html_list.append('<td>{}</td>'.format(tape[len(tape.string)]))
	return '<table class="tape"> {} </table>'.format(''.join(html_list))


# helpers
def allowed_file(filename:str):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clean_str(s: str):
	s.translate(str.maketrans({' ':'', '\n':''}))


def set2str(s):
	res = ''
	i = 0
	for item in s:
		if i == len(s)-1:
			res += item
		else:
			res += item + ', '
		i += 1
	return res


class TMForm(Form):
	description = StringField('Description')
	states = StringField('Allowable States', [validators.input_required])
	terminating_states = StringField('Terminating States', [validators.input_required])
	start_state = StringField('Start State', [validators.input_required])
	blank_symbol = StringField('Blank Symbol')
	tape_symbols = StringField('Tape Symbols')
	# input_letters = StringField('')
	tape = StringField('Tape')
	trans_funcs = TextAreaField('Transforming Functions',[validators.input_required])
