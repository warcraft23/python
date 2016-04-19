__author__ = 'Edward'

from flask import *

import pymongo
import bson
import uuid

db = pymongo.MongoClient("localhost", 27017).test

form = """
<html><head></head><body>
<form method="POST">
<input type="text" name="username" placeholder="Username">
<input type="text" name="password" placeholder="Password">
<input type="text" name="firstname" placeholder="Firstname">
<input type="text" name="lastname" placeholder="Lastname"/>
<input type="text" name="age" placeholder="Age">
<input type="submit" value="Submit">
</form></body></html>
    """


app = Flask(__name__)
app.secret_key = "secret"

@app.route("/logout/")
def logout():
    session.pop("_id")
    return redirect("/login/")

@app.route("/")
def index():
    if "_id" not in session:
        return redirect("/login/")
    name = request.args.get("name")
    lastname = request.args.get("lastname")
    if not name:
        return "<h1>Search for someone</h1><form method='GET'><input name='name' type='text' placeholder='First Name'><input name='lastname' type='text' placeholder='Last Name'><input type='submit'></form>"
    else:
        search_results = db.members.find_one({"{}".format(name):lastname})
        if search_results:
            search_results = name + " " + lastname + " is " + search_results['account_info']['age'] + " years old."
        return "{}<form><input name='name' type='text' placeholder='First Name'><input name='lastname' type='text' placeholder='Last Name'><input type='submit'></form>".format(search_results)

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        check = db.members.find_one({"username":username, "password":password})
        if check:
            session['_id'] = str(check)
            return redirect("/?name={}".format)
        else:
            return "Invalid Login"
    return "<h1>Login</h1>" + form

@app.route("/signup/", methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']
        age = request.form['age']
        session['_id'] = str(db.members.insert({
            "username":username,
            "password":password,
            firstname:lastname,
            "account_info":{
                "age":age,
                "age":age,
                "isAdmin":False,
                "secret_key":uuid.uuid4().hex
            }
        }))
        return redirect("/")
    return "<h1>Signup</h1>" + form

@app.route("/settings/", methods=['GET', "POST"])
def settings():
    if request.method == "POST":
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']
        age = request.form['age']
        db.members.update({"_id":bson.ObjectId(session['_id'])}, {"$set":{
            "{}".format(firstname):lastname,
            "account_info.age":age,
            "username":username
        }})
        return "Values have been updated!"
    return "<h1>Settings</h1>" + form

@app.route("/admin/", methods=['GET', 'POST'])
def admin():
    if "_id" not in session:
        return redirect("/login/")
    theUser = db.members.find_one({"_id":bson.ObjectId(session['_id'])})
    if not theUser['account_info']['isAdmin']:
        return "You do not have access to this page."
    if request.method == "POST":
        secret = request.form['secret_key']
        return str(db.members.find_one({"account_info.secret_key":secret}))
    return """<h1>Search user by secret key</h1>
    <form method="post"><input type="text" name="secret_key" placeholder="Secret Key"/><input type="submit" value="Serach"/></form>
    """

app.run(debug=True)