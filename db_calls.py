''' Andrea Mock - module that includes functions 
that make calls to the database
'''

# import database
import cs304dbi as dbi

# login and logout functionalities
def checkLoginCredentials(conn, user):
    """returns the username and password (hashed) for a given username"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select user_id, hashed from user_accounts where username=%s ''', [user])
    return curs.fetchone()



def findUser(conn, username):
    """checks if a particular username already exist, if yes 
    returns that user"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from user_accounts where username=%s ''', [username])
    return curs.fetchone()

def registerUser(conn, username, passwd, email):
    """checks if login credentials exist a"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''INSERT INTO user_accounts (user_id, username, hashed, email) 
    VALUES (null, %s, %s, %s)''', [username, passwd, email])
    conn.commit()
    print('user added successfully!')

    curs.execute('select last_insert_id() as id')
    row = curs.fetchone()
    return row['id']


""" def getLastId(conn):
    returns the last id that a user was given 
    curs = dbi.dict_cursor(conn)
    curs.execute('select last_insert_id()')
    row = curs.fetchone()
    uid = row[0]
    return uid """


# adding albums and songs

""" def addMusic(conn, ):
    # adds a music title to the music table
    curs = dbi.dict_cursor(conn)
    curs.execute('''INSERT INTO all_music (title, artist, genre, description, filename) 
    VALUES (%s, %s, %s)''', [username, password, email])
    
    conn.commit()
    print('user added successfully!') """
    

