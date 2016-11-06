from flask import Flask, render_template, request, redirect, session, flash
import re
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
    # elif re.match(EMAIL_REGEX,request.form['email']):  #regex broken
    #     errors.append("Not a valid email")
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
    messagequery = "SELECT * FROM messages LEFT JOIN users ON users.id = messages.users_id"
    messagedata = mysql.query_db(messagequery)

    #query for comments
    commentquery = "SELECT * FROM comments LEFT JOIN messages ON comments.messages_id = messages.id"
    commentdata = mysql.query_db(commentquery)


    return render_template('wall.html', messagedata = messagedata, commentdata= commentdata)


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

@app.route('/comment',methods=["POST"])
def comment():
    # adds comment info to db w/query
    return redirect('/wall')

@app.route('/delete')
def delete():
    # delete message
    return redirect('/wall')

@app.route('/logoff')
def logoff():
    session.clear()
    return redirect('/')

app.run(debug=True) # run our server
