from gui import app
import threading
import time
import webbrowser


def open_app():
	url = 'http://127.0.0.1:5000/'
	print('app startint...(in 5 seconds)')
	time.sleep(5)
	webbrowser.open(url)


threading.Thread(target=open_app).start()
app.run(debug=True)
