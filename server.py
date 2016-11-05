from flask import Flask, render_template, request, redirect, session, flash
import re
from mysqlconnection import MySQLConnector

app = Flask(__name__)
mysql = MySQLConnector(app,'mydb')

app.secret_key = 'whatsinside'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
    # login / register page
    return render_template('index.html')

@app.route('/register')
def register():
    # adds user info to database
    return render_template('wall.html')

@app.route('/login')
def login():
    # logs user in / sets session user id
    return render_template('wall.html')

@app.route('/wall')
def wall():
    # refresh wall content
    return render_template('wall.html')

@app.route('/message')
def message():
    # adds message info to db w/query
    return redirect('/wall')

@app.route('/comment')
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
