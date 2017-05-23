from flask import Flask, render_template
from turing_machine import TuringMachine, Tape

app = Flask(__name__)

# 由于这个应用作为一个演示图灵机的工具，并没有并发的需求，所以我在这里使用了指向一个图灵机的全局变量
# tm初始是演示用图灵机，把纸带上的所以0改成1
trans_funcs = '''f(q0, 0) = (q0, 1, R);
				f(q0, 1) = (q0, 1, R);
				f(q0, B) = (q1, B, S);
				'''
states = {'q0', 'q1'}
start_state = 'q0'
termin_states = {'q1'}

tm = TuringMachine(states, start_state, termin_states, trans_funcs, tape='0010101')

g = 0

@app.route('/')
def hello_world():
	global  g
	g += 1
	return 'Hello World!' + str(g)


@app.route('/tm')
def tm_gui():
	global tm
	tape_html = tape2html(*tm.current_tape_pos)
	tm.step_forward()
	return render_template('tm.html', tape_html=tape_html)


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

if __name__ == '__main__':
	app.run(debug=True)
