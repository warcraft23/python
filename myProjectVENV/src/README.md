#Flask
##路由
###HTTP方法
- GET 浏览器通知服务器只获取页面上的信息并且发送回来。这可能是最常用的方法
- HEAD 浏览器告诉服务器获取信息，但是只对头信息感兴趣，不需要整个页面的内容。应用应该处理起来像接收到一个GET请求但是不传递实际内容。在Flask中你完全不需要处理它，底层的Werkzeug库会为我处理。
- POST 浏览器通知服务器它要在URL上提交一些信息，服务器必须保证数据被存储且只是存储一次。这是HTML表单通常发送数据到服务器的方法。
- PUT 同POST类似，但是服务器可能触发了多次存储过程，多次覆盖掉了旧值。考虑到传输过程中连接丢失，在该情况下浏览器和服务器之间的系统可能安全地第二次接受请求，而不破坏其他东西。对于POST是不可能实现的，因为他只触发一次。
- DELETE 移除给定位置的信息
- OPTIONS 给客户端提供一个快速的途径来指出这个URL支持哪些HTTP方法

###课后习题
```
@app.route('/sum/<int:a>/<int:b>')
def sum(a,b):
	return '%d' % (a+b)
```

##渲染模板和静态文件
###课后作业
利用flask的静态文件和模板，显示一个绿色的Hello Shiyanlou字样

修改hello.py文件为

```
@app.route('/hello/')
@app.route('/hello/<username>')
def hello(username=None):
	greenCSS=url_for('static',filename='css/green.css')
	return render_template('hello.html',css=greenCSS,name=username)
```

然后创建static下的css文件夹和templates文件夹，css里存放css文件，teplates里面存模板

css文件如下

```
.shiyanlou{
	color:green;
}
```

模板文件如下

```
<!DOCTYPE html>
<head>
	<link rel="stylesheet" type="text/css" href="{{ css }}">
	<title>Hello From Flask</title>
</head>
<body>
	{% if name %}
	<div class='shiyanlou'><h1>Hello {{ name }}</h1></div>
	{% else %}
	<h1>Hello World!</h1>
	{% endif %}
</body>
```

