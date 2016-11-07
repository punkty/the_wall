from flask import Flask, render_template, request, redirect, session, flash
import re
import datetime
from datetime import timedelta
import math
from mysqlconnection import MySQLConnector
from flask_bcrypt import Bcrypt

app = Flask(__name__)
mysql = MySQLConnector(app,'walldb')
bcrypt = Bcrypt(app)

app.secret_key = 'whatsinside'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
    # login / register page
    return render_template('index.html')

@app.route('/register', methods=["POST"])
def register(): #check for redundancy
    # adds user info to database
    errors = []

    query = "SELECT * FROM users WHERE email = :email;"
    data = {"email": request.form["email"]}
    user = mysql.query_db(query,data)

    if not request.form['first_name']:
        errors.append("Please enter a first name")

    if not request.form['last_name']:
        errors.append("Please enter a last name")

    if not request.form['email']:
        errors.append("Please enter an email")
    elif not re.match(EMAIL_REGEX,request.form['email']):
        errors.append("Not a valid email")
    elif user:
        errors.append("Email is already in use")

    if not request.form['password']:
        errors.append("Please enter a password")
    elif len(request.form['password']) < 8:
        errors.append("Password must be at least 8 characters")
    elif request.form['password'] != request.form["confirm"]:
        errors.append("Password must match")

    if errors:
        for error in errors:
            flash(error)
        return redirect("/")
    else:
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :pw_hash, NOW(), NOW())"
        data = {
            "first_name": request.form["first_name"],
            "last_name": request.form["last_name"],
            "email": request.form["email"],
            "pw_hash": bcrypt.generate_password_hash(request.form["password"])
        }
        session["user_id"] = mysql.query_db(query,data)

        return redirect("/wall")

@app.route('/login',methods=["POST"])
def login():
    # logs user in / sets session user id
    query = "SELECT * FROM users WHERE email=:email;"

    data = {"email": request.form["email"]}

    user = mysql.query_db(query,data)

    if not user:
        flash("User name or password not valid")
        return redirect('/')
    
    user = user[0]

    if bcrypt.check_password_hash(user["password"], request.form["password"]):  #is password  matched correctly
        session["user_id"] = user["id"]
        return redirect('/wall')
    else:
        flash("User name or password not valid")
        return redirect('/')


@app.route('/wall')
def wall():
    # refresh wall content
    #query for messages
    if "user_id" not in session and request.endpoint != "/": #ask Jack about this
        return redirect('/')

    userquery = "SELECT first_name FROM users WHERE id = :id;"

    data = {"id":session["user_id"]}

    user_first = mysql.query_db(userquery,data)[0]


    messagequery = "SELECT messages.id, messages.users_id, messages.message, messages.created_at, users.first_name, users.last_name FROM messages LEFT JOIN users ON users.id = messages.users_id ORDER BY messages.created_at DESC"
    messagedata = mysql.query_db(messagequery)

    #query for comments
    commentquery = "SELECT comments.id, comments.comment, comments.created_at, comments.messages_id, comments.users_id, users.first_name, users.last_name FROM comments LEFT JOIN messages ON comments.messages_id = messages.id LEFT JOIN users  ON comments.users_id = users.id ORDER BY comments.created_at DESC"
    commentdata = mysql.query_db(commentquery)


    return render_template('wall.html', messagedata = messagedata, commentdata= commentdata, user_first=user_first)


@app.route('/message',methods=["POST"])
def message():
    # adds message info to db w/query
    query = "INSERT INTO messages(users_id, created_at, message)VALUES(:users_id, NOW(), :message)"
    data = {
        "users_id" : session['user_id'],
        'message' : request.form['new_message']
    }
    mysql.query_db(query,data)

    return redirect('/wall')

@app.route('/comment/<message_id>',methods=["POST"])
def comment(message_id):
    query = 'INSERT INTO comments (comment, messages_id, users_id, created_at) VALUES (:comment, :messages_id, :users_id, NOW());'
    data = {
            'comment': request.form['new_comment'],
            'messages_id': message_id,
            'users_id': session['user_id']
    }
    mysql.query_db(query,data)
    return redirect('/wall')

@app.route('/delete/<id>')
def delete(id):
    if "user_id" not in session and request.endpoint != "/": #ask Jack about this
        return redirect('/')
        
    query = "SELECT created_at FROM messages WHERE id = :id"

    data = {'id':id}    
    #DATETIMEISSOMEHORSESHIT
    # if (datetime.datetime.time(time_stamp) timedelta(minutes = 30) > datetime.datetime.now().time()):
    query = "DELETE FROM comments WHERE comments.messages_id = :id; DELETE FROM messages WHERE messages.id = :id;"
    data = {"id":id}
    mysql.query_db(query,data)
    return redirect('/wall')
    # else:
    #     flash("30 minutes has passed")
    #     return redirect ('/wall')
       

    # delete message

@app.route('/logoff')
def logoff():
    session.clear()
    return redirect('/')

app.run(debug=True) # run our server
