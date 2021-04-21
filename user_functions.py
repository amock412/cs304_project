#user_functions.py - implementation of routes pertaining to the user
# CS304 Project MusicShare 
# Andrea Mock

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename

from app import app, notLoggedIn

import cs304dbi as dbi
import db_calls # import module that makes database calls
import music # 

def renderPersonalProfile(userInfo,conn):
    """helper function that handles user accessing
    their own profile"""
    # get people user is following
    usersFollowing = db_calls.following(conn, session['user_id']) 

    # if user is not following anyone render follow people text 
    if usersFollowing is None: 
        return render_template('personal-profile.html', title='Personal Profile', 
        user=userInfo)
    return render_template('personal-profile.html', title='Personal Profile', 
        user=userInfo, follow=usersFollowing)

@app.route('/user/<int:uid>')
def user(uid):
    """ displays a users information"""
    if notLoggedIn(): # check if user is logged in 
        return redirect( url_for('index'))

    conn = dbi.connect()
    userInfo = db_calls.getUserInfo(conn, uid)
    
    # if a person tries to access page of user that does not exist reroute to users
    if userInfo is None: 
        flash('The user you are trying to find does not exist')
        return redirect( url_for('all_users'))

    # if trying to access own profile renders personal profile
    if uid == session['user_id']:
        return renderPersonalProfile(userInfo,conn)
    
    # check if logged in user is following that user
    following = db_calls.checkRelationship(conn,session['user_id'], uid)

    # if something is returned then show possibility of unfollowing person
    if following is not None:
        return render_template('user.html',title='User Profile', user=userInfo, following=True)

    return render_template('user.html',title='User Profile', user=userInfo)

@app.route('/delete/', methods=['POST'])
def delete_account(): 
    if notLoggedIn(): 
        return redirect( url_for('index'))

    try:
        uid = session['user_id']
        conn = dbi.connect()
        db_calls.deleteUser(conn,uid) # delete the user
        return redirect(url_for('logout'))
    except Exception:
            flash('Failed to delete account')
            return render_template('user.html',title='User Profile')
    

@app.route('/update_profile/<int:uid>', methods=['GET', 'POST'])
def update_profile(uid): 

    # check is user is logged in 
    if notLoggedIn(): 
        return redirect( url_for('index'))

    # allow users to only update their own profile
    if uid != session['user_id']:
        flash('''You can only update your own profile, but feel 
        free to check out other users.''')
        return redirect(url_for('all_users'))

    conn = dbi.connect()
    userInfo = db_calls.getUserInfo(conn, uid)


    if request.method == 'POST':
    
        try:
        # update userinfo if new data is ok 
            db_calls.updateUser(conn, uid, request.form['email'], 
            request.form['name'],request.form['description'])
            
            return redirect(url_for('user', uid=uid))
        except Exception:
            flash('Failed to update account')
            return redirect(url_for('user', uid=uid))
    return render_template('update-profile.html',title='Update Profile', user=userInfo)

@app.route('/all_users/')
def all_users(): 

    if notLoggedIn(): 
        return redirect( url_for('index'))

    try:
        conn = dbi.connect()
        allUsers = db_calls.getAllUsers(conn)
        return render_template('all-users.html',title='Users', all_users=allUsers)
    except Exception:
        flash('Failed to display all users')
        return redirect(url_for('home'))

def renderUserResults(conn, query):
    """given a query looks for that username in the database
    and returns the results, be either redirecting to that 
    users page, showing an error or listing all users matching 
    the query"""
    results = db_calls.findUsers(conn, query)
    if len(results) == 0: # no results found, display
        return render_template('search-error.html',type='user', title='Search error')
    elif (len(results) == 1): # redirects to that user's page
        return redirect(url_for('user',  uid= results[0]['user_id']))
    else:
        return render_template('list.html', type = 'user', all_things = results, 
        query= query, title="User Results")

@app.route('/user_lookup/')
def user_lookup():
    """ processes the search for either a music title or an artist """
    query = request.args.get('query')
    conn = dbi.connect()
    # extract users from db that match query 
    return renderUserResults(conn, query)

@app.route('/follow_user/<int:uid>')
def follow_user(uid):
    """ processes a user starting to follow another user"""
    # adds follower-followee data to database table
    conn = dbi.connect()
    db_calls.followUser(conn, session['user_id'], uid) 
    return redirect(url_for('user', uid=uid))

@app.route('/unfollow_user/<int:uid>')
def unfollow_user(uid):
    """ processes a user unfollowing another user"""
    # deletes follower-followee data to database table
    conn = dbi.connect()
    db_calls.deleteFollowUser(conn, session['user_id'], uid) 
    return redirect(url_for('user', uid=uid))


@app.route('/user_pic/')
def userImage():
    """ grabs the image that is used for nice styling of user/artist cards"""
    return send_from_directory(app.config['UPLOADS'],'musical_note.png')

