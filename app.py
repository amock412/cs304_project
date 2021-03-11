from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
import db_calls # import module that makes database calls

import random 
import re # used to check if input is in valid format
import bcrypt # for security

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True


# for file upload
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

def allowed_file(filename):
    """ determine if file is in allowed format type """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('base.html',title='Login')

@app.route('/login/', methods=['GET','POST'])
def login(): 
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            # save username and password
            username = request.form['username']
            password = request.form['password']

            # connect to database and check if user exists and credentials correct
            conn = dbi.connect()
            userInfo = db_calls.checkLoginCredentials(conn, username)

            if userInfo is None:
            # show error as user not found 
                flash('Login incorrect. Please try again or register')
                return redirect( url_for('index'))
            
            hashed = userInfo['hashed']
            print('database has hashed: {} {}'.format(hashed,type(hashed)))
            print('form supplied passwd: {} {}'.format(password,type(password)))

            hashed2 = bcrypt.hashpw(password.encode('utf-8'),hashed.encode('utf-8'))
            hashed2_str = hashed2.decode('utf-8')
            print('rehash is: {} {}'.format(hashed2_str,type(hashed2_str)))
            if hashed2_str == hashed:
                print('they match!')
                flash('successfully logged in as '+username)
                session['username'] = username
                session['user_id'] = userInfo['user_id']
                session['logged_in'] = True
                return redirect( url_for('home') )
            else:
                flash('Incorrect login, please try again or register')
                return redirect( url_for('index'))
    return render_template('login.html',title='Login')

@app.route('/logout/')
def logout(): 
    try:
        if 'username' in session:
            # get rid of session info 
            session.pop('logged_in')
            session.pop('user_id')
            session.pop('username')
            flash('You are logged out')
            # redirect to the login page 
            return redirect(url_for('index'))

        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('index') )

    except Exception as err:
        flash('An error occured '+str(err))
        return redirect( url_for('index') )

    

def checkValidInput(username, email): 
    """checks if the username and email have the correct formatting"""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) and re.match(r"[A-Za-z0-9]+", username)


@app.route('/register/', methods=['GET','POST'])
def register(): 
    if request.method == 'POST':
        # creates a new user if all fields are filled in 
        try: 
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hashed_str = hashed.decode('utf-8')

            print(password, type(password), hashed, hashed_str)


            if checkValidInput(username, email): 
                conn = dbi.connect()
                try: 
                    # try adding user to user table
                    uid = db_calls.registerUser(conn,username, hashed_str, email)
                except Exception() as err:
                    print('That username is taken: {}'.format(repr(err)))
                    return redirect(url_for('index'))
                
                # get user id
                #currentUser = db_calls.findUser(conn, username)
                #currentUser['user_id']
                #uid = db_calls.getLastId(conn)
                print('user id is', uid)
                # save information in session
                session['username'] = username
                session['user_id'] = uid
                session['logged_in'] = True
                print('im here')
                return redirect( url_for('home') )
            
        except Exception as err:
            flash('form submission error '+str(err))
            return redirect( url_for('index') )

    return render_template('register.html',title='Register')


@app.route('/home/')
def home(): 
    username = session['username']
    return render_template('home.html',title='Home', user=username)

@app.route('/upload/',methods=['GET', 'POST'])
def upload(): 
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template('music-upload.html',title='Upload music')



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