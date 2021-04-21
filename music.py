# music.py - getting information about music in database
# adding albums and songs
# CS304 Project MusicShare 
# Andrea Mock

# import database
import cs304dbi as dbi

def addMusic(conn, title, artist, genre, description, filename, user ):
    """ adds a music title to the music table and returns the id
    of the newly added music item"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''INSERT INTO all_music 
    (mid, user_id, title, aid, genre, description, filename) 
    VALUES (null, %s, %s, %s,  %s, %s,  %s)''', 
    [user, title, artist, genre, description, filename])
    conn.commit()
    print('music added successfully!')
    # grab last id for further processing
    curs.execute('select last_insert_id() as id')
    row = curs.fetchone()
    last_id = row['id']
    return last_id

def getAllMusic(conn): 
    """ grabs all the music currently in the database and returns 
    the music title, genre, description, artist name, user who added the 
    title, and filename of the connected file
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from picfile inner join all_music 
    using (mid) left outer join artists using (aid) order by title''')
    return curs.fetchall()

def getImage(conn, mid):
    """ grabs the filename of the file relating to a music file to 
    display them together later on"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select filename from picfile where mid = %s''',
        [mid])
    return curs.fetchone()

def getMyMusic(conn, userId):
    """ returns all the music titles added by a particular user"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select mid, title, genre, name, aid, description
    from picfile inner join all_music using (mid) left outer join artists 
    using (aid) where all_music.user_id =%s''', [userId])
    return curs.fetchall()

def getMusicByTitle(conn, musTitle):
    """ given the name of a music title returns the results for the query"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from all_music left outer join artists 
    using (aid)where title like %s''', ['%' + musTitle + '%'])
    return curs.fetchall()

def getMusicByGenre(conn, genre):
    """ given the name of a genre, returns all titles that fall under that genre"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from all_music left outer join artists using (aid)
    where genre= %s''', [genre])
    return curs.fetchall()

def getMusicByArtist(conn, artist):
    """ given the name of an artist, returns all titles that are 
    by a particular artist"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from all_music inner join artists using (aid) 
    where name like %s''', ['%' + artist +'%'])
    return curs.fetchall()

def getArtist(conn, artistName):
    """ given the name of an artist, returns the artists name and aid"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select distinct aid, name from artists
    where name like %s''', ['%' + artistName +'%'])
    return curs.fetchall()

def getArtists(conn):
    """ retrieves all the artists and their names from the 
    artists table"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select distinct * from artists order by name''')
    return curs.fetchall()

def getMusicByArtistId(conn, aid):
    """gets an artists music by their artist id (aid) """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from all_music left outer join artists 
    using (aid) where aid = %s ''', [aid])
    return curs.fetchall()
    
def deleteMusic(conn,mid):
    """ deletes a music title with a particular music id """
    curs = dbi.dict_cursor(conn)
    curs.execute('''delete from all_music where mid= %s''', [mid])
    conn.commit()
    print('music title successfully deleted')

def getSingleMusicTitle(conn, mid):
    """grabs the music title that has a particular music id and returns that item"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select *
                    from picfile inner join all_music using (mid) 
                    left outer join artists using (aid) where 
                    mid = %s''', [mid])
    return curs.fetchone()

def updateMusicTitle(conn, mid, title, artist, genre, description):
    """given a music id updates the music title's information """
    curs = dbi.dict_cursor(conn)
    print('in the process of updating music')
    curs.execute('''update all_music set title= %s, aid=%s, 
    genre = %s, description = %s where mid=%s ''', 
    [title, artist, genre, description, mid])
    conn.commit()
    print('updated music info successfully')

def getArtistById(conn, aid):
    """gets an artists info by their artist id (aid) """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from artists where aid = %s ''', [aid])
    return curs.fetchone()

def getArtistByName(conn, name):
    """ given an artists name checks if they are part of the artists in our database
    and returns their info"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from artists where name = %s ''', [name])
    return curs.fetchone()

def addArtist(conn, name, uid):
    """ given an artists name inserts that artist into the artists database table
    and returns the id of the newly added artist"""
    curs = dbi.dict_cursor(conn)
    curs.execute('''INSERT INTO artists (aid, name, user_id) VALUES (null, %s, %s)''', 
    [name, uid])
    print('artist added successfully')
    # grab the artist id for further processing
    curs.execute('select last_insert_id() as id')
    row = curs.fetchone()
    return row['id']
