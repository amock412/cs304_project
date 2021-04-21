# app.py - general Flask app with routes 
# CS304 Project MusicShare 
# Andrea Mock

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
import db_calls # import module that makes database calls
import music

import random 
import re # used to check if input is in valid format
import bcrypt # for security
import os

app.secret_key = 'secret_key'
# replace that with a random key
""" app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ]) """

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True


# for file upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOADS'] = 'uploads'
app.config['MAX_FILESIZE'] = 1*1024*1024 # 1 MB, max upload filesize


def allowed_file(filename):
    """ determine if file is in allowed format type """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_filesize(filesize):
    """ determines if the filesize is too large, return true if file size is ok otherwise false"""
    return int(filesize) <= app.config["MAX_FILESIZE"]

def notLoggedIn():
    """ checks if a user is logged in"""
    return session.get('logged_in') != True 
    
@app.route('/')
def index():
    """first page is welcome page"""
    if session.get('logged_in') == True:
        return redirect( url_for('home'))
    return render_template('index.html',title='MusicShare')

def checkLoginCredentials(userInfo, password):
    """ helper function that checks the password in the 
    database table matches the one submitted, returns true if 
    passwords match
    """
    hashed = userInfo['hashed'] # password from db
    hashed2 = bcrypt.hashpw(password.encode('utf-8'),hashed.encode('utf-8'))
    hashed2_str = hashed2.decode('utf-8')
    return hashed2_str == hashed
            

@app.route('/login/', methods=['GET','POST'])
def login(): 
    """ displays the login page as well as checks the login credentials, 
        if entered correctly the user is rerouted to the logged in home page
    """
    if not notLoggedIn(): # redirect to logged in portion of site if logged in 
        flash('You have already successfully logged in!')
        return redirect( url_for('home'))

    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            # save username and password
            username = request.form['username']
            password = request.form['password']

            # connect to database and check if user exists and credentials correct
            conn = dbi.connect()
            userInfo = db_calls.retrieveLoginCredentials(conn, username)

            if userInfo is None:
            # show error as user not found 
                flash('Username is incorrect. Please try again or register')
                return redirect( url_for('login'))
            
            if checkLoginCredentials(userInfo, password):
                print('they match!')
                flash('successfully logged in as '+username)
                session['username'] = username
                session['user_id'] = userInfo['user_id']
                session['logged_in'] = True
                return redirect( url_for('home') )
            else:
                flash('Incorrect login, please try again or create an account')
                return redirect( url_for('login'))
    return render_template('login.html',title='Login')

@app.route('/logout/')
def logout(): 
    """ logs out a user and deletes the session information """
    try:
        if 'username' in session:
            # get rid of session info 
            session.pop('logged_in')
            session.pop('user_id')
            session.pop('username')
            flash('You have successfully logged out')
            # redirect to the login page 
            return redirect(url_for('index'))

        else:
            flash('You are not logged in. Please login or create an account')
            return redirect( url_for('index') )

    except Exception as err:
        flash('An error occurred '+str(err))
        return redirect( url_for('index') )


def checkInputFormat(username, email): 
    """checks if the username and email have the correct formatting"""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) and re.match(r"[A-Za-z0-9]+", username)


@app.route('/register/', methods=['GET','POST'])
def register(): 
    """allows a user to create an account and once created 
    routes the user to the logged-in home page 
    """
    if session.get('logged_in') == True:
        return redirect( url_for('home'))
        
    if request.method == 'POST':
        # creates a new user if all fields are filled in 
        try: 
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hashed_str = hashed.decode('utf-8')

            print(password, type(password), hashed, hashed_str)

            if checkInputFormat(username, email): 
                conn = dbi.connect()
                try: 
                    # try adding user to user table
                    uid = db_calls.registerUser(conn,username, hashed_str, email)
                    
                except Exception as err:
                    print('That username is taken: {}'.format(repr(err)))
                    flash('''The username '''  + username + ''' is already taken, 
                    please use a different username.''')
                    return redirect(url_for('register'))
                
                print('user id is', uid)
                # save information in session
                session['username'] = username
                session['user_id'] = uid
                session['logged_in'] = True
                flash('successfully logged in as '+username)
                return redirect( url_for('home') )
            
        except Exception as err:
            flash('form submission error '+str(err))
            return redirect( url_for('register') )

    return render_template('register.html',title='Register')

@app.route('/home/')
def home(): 
    """ renders home page that is displayed when a user is logged in"""
    if session.get('logged_in') != True:
        return redirect( url_for('index'))
    return render_template('home.html',title='Home')


# import modules that implemented user and music routes 
from user_functions import *
from music_functions import *

# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    if notLoggedIn():
        flash('Page was not found')
        return render_template("index.html")
    return render_template("error.html", title='Error')


@app.before_first_request
def init_db():
    dbi.cache_cnf()
    dbi.use('am10_db') 


if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)