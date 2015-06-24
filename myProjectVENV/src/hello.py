from flask import Flask
app= Flask(__name__)
@app.route('/')
def hello_world():
	return "Hello World!"

@app.route('/shiyanlou')
def printMyName():
	return "I'm Edward!"

if __name__=='__main__':
	app.debug=True
	app.run()

