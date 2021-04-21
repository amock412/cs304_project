''' 
db_calls.py - module that includes functions 
that make calls to the database for user information, and 
following, deleting, logging in a user
CS304 Project MusicShare 
Andrea Mock
'''

# import database
import cs304dbi as dbi

# login and logout functionalities
def retrieveLoginCredentials(conn, user):
    """returns the username and password (hashed) for a given username"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select user_id, hashed 
    from user_accounts where username=%s ''', [user])
    return curs.fetchone()

def findUser(conn, username):
    """checks if a particular username already exist, if yes 
    returns that user"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from user_accounts where username=%s ''', [username])
    return curs.fetchone()

def registerUser(conn, username, passwd, email):
    """checks if login credentials exist and returns the id of the 
    newly inserted user"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''INSERT INTO user_accounts (user_id, username, hashed, email) 
    VALUES (null, %s, %s, %s)''', [username, passwd, email])
    conn.commit()
    print('user added successfully!')
    # retrieves the id of the newly created user
    curs.execute('select last_insert_id() as id')
    row = curs.fetchone()
    uid = row['id']
    return uid

def insert_image_file(conn, filename, mid):
    '''Insert filename into the picfile table under key mid'''
    curs = dbi.cursor(conn)
    try:
        curs.execute('''insert into picfile(mid,filename) 
        values (%s,%s)''',[mid,filename])
        conn.commit()
    except Exception as err:
        print('Exception on insert of {}: {}'.format(filename, repr(err)))


def getUserInfo(conn, uid):
    """given a person's user id retrieve their information""" 
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from user_accounts where user_id=%s ''', [uid])
    return curs.fetchone()

def deleteUser(conn,uid):
    """given a user's id deletes the user from the database table"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''delete from user_accounts where user_id=%s ''', [uid])
    conn.commit()
    print('deleted user successfully')

def updateUser(conn,uid, email, name, description):
    """given a user's id updates the user's information """
    curs = dbi.dict_cursor(conn)
    print('in the process of updating user')
    curs.execute('''update user_accounts 
    set email = %s, name = %s, description = %s 
    where user_id=%s ''', [email, name, description, uid])
    conn.commit()
    print('updated user info successfully')

def getAllUsers(conn):
    """retrieves all the users that have an account in MusicShare"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from user_accounts order by username''')
    return curs.fetchall()

def findUsers(conn, username):
    """checks if a users matching the given username  exist, returns 
    all users matching that username """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from user_accounts where username like %s ''', 
    ['%' + username + '%'])
    return curs.fetchall()

def followUser(conn, follower, followee):
    """ adds a follower, followee relationship when a user starts following 
    another user"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''INSERT INTO music_friends (follower, followee) values 
    (%s, %s) ''', [follower, followee])
    conn.commit()
    print('friend relationship added successfully!')


def deleteFollowUser(conn, follower, followee):
    """ deletes a follower, followee relationship when a user stops following 
    another user"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''delete from music_friends 
    where follower=%s and followee=%s''', [follower, followee])
    conn.commit()
    print('deleted friend relationship  successfully')

def checkRelationship(conn, follower, followee):
    """ checks if a user is following another user and
    returns their relationship if yes"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from music_friends where 
    follower=%s and followee=%s''', [follower, followee])
    return curs.fetchone()

def following(conn, user):
    """ returns all the users a particular user is following"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from music_friends join user_accounts 
    on music_friends.followee=user_accounts.user_id 
    where follower=%s''', [user]) 
    return curs.fetchall()