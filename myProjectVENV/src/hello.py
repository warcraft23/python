from flask import Flask
app= Flask(__name__)
@app.route('/')
def hello_world():
	return "Hello World!"

@app.route('/shiyanlou')
def printMyName():
	return "I'm Edward!"

@app.route('/user/<username>')
def show_user_profile(username):
	return 'User %s' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
	return 'Post_ID %d' % post_id

@app.route('/projects/')
def projects():
	return 'Projects Hello!'

@app.route('/about')
def about():
	return 'About Hello!'


if __name__=='__main__':
	app.debug=True
	app.run()

