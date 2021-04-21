# music_functions.py
# CS304 Project MusicShare 
# Andrea Mock
# additional module where the routes used to get, add and update music are implemented

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename

from app import (app, allowed_filesize, notLoggedIn, allowed_file)

import os
import cs304dbi as dbi
import db_calls # import module that makes general database calls
import music # imports module that makes database calls specifically music ones
import uuid # to create a universally unique identifier to save files in unique way


def checkArtistStatus(conn, artistName):
    """helper function that adds a new artist to the 
    artist database table, if the artist already exists 
    retrieves their artist info and returns the artist id
    """ 
    curs = dbi.dict_cursor(conn)
    curs.execute('lock tables artists write, all_music write')
    artistInfo = music.getArtistByName(conn, artistName)
    if artistInfo is None: 
        aid = music.addArtist(conn, artistName, session['user_id'])
    else:
        aid = artistInfo['aid']
    curs.execute('unlock tables')
    return aid 

def saveFile(imageFile, musicFilename):
    """ helper function that saves a file to the filesystem given the file 
    from the form and the file name """
    ext = musicFilename.split('.')[-1]
    fName = uuid.uuid4() # creates a unique file name 
    # saves filename with corresponding extension
    filename = secure_filename('{}.{}'.format(fName,ext))     
    pathname = os.path.join(app.config['UPLOADS'],filename)
    imageFile.save(pathname)   
    return filename 

@app.route('/upload/',methods=['GET', 'POST'])
def upload(): 
    """ displays and processes music uploads to the database"""

    if notLoggedIn(): # check if user is logged in
        return redirect( url_for('index'))

    if request.method == 'POST':
        # check if the post request has the file part
        try: 
            if request.files:
                if "filesize" in request.cookies:
                    if not allowed_filesize(request.cookies["filesize"]):
                        print("Filesize exceeded maximum limit")
                        return redirect(request.url)
                    
                    f = request.files['pic']
                    music_filename = f.filename

                    # checking if no file was added and if file extension is allowed
                    if (music_filename == '') or (not allowed_file(music_filename)):
                        flash('''Error with file, check if you added a file or if your 
                        file has the endings .jpeg, .jpg, .png or .gif''')
                        return redirect(request.url)

                    # saves file in filesystem and returns filename
                    filename = saveFile(f, music_filename)     
                
            else: 
                flash('Error with file, check if you added a file')
                return redirect(request.url)
            
            conn = dbi.connect()

            # checks if a new artist was entered as artist 
            aid = checkArtistStatus(conn, request.form['artist'])

            # adds music title to all music table
            musicId = music.addMusic(conn, request.form['title'], aid, 
            request.form['genre'], request.form['description'], filename, 
            session['user_id'])
            # insert file information into file table 
            db_calls.insert_image_file(conn, filename, musicId)
            flash('Upload successful')
            return render_template('music-upload.html',title='Upload music')      

        except Exception as err:
            flash('Upload failed {why}'.format(why=err))
            return render_template('music-upload.html',title='Upload music')

    return render_template('music-upload.html',title='Upload music')

@app.route('/pic/<mid>')
def pic(mid):
    """ grabs the image that corresponds to a particular music item"""
    conn = dbi.connect()
    musicFile = music.getImage(conn,mid)
    if musicFile is None:
        return redirect(url_for('index'))
    return send_from_directory(app.config['UPLOADS'],musicFile['filename'])

@app.route('/allmusic/')
def all_music():
    """ displays all the music in the database"""
    if notLoggedIn(): # check if logged in
        return redirect( url_for('index'))
    conn = dbi.connect()
    allMusic = music.getAllMusic(conn)
    return render_template('all-music.html',all_music =allMusic, title='All Titles')

@app.route('/mymusic/')
def my_music():
    """ displays the music titles that were added by the particular
    logged in user """

    # checks if user is logged in, if not redirects to welcome page
    if notLoggedIn(): 
        return redirect( url_for('index'))
    # gets the music by a particular user from the database
    conn = dbi.connect()
    uid = session['user_id']
    myMusic = music.getMyMusic(conn, uid)
    # if user hasn't added any music display add music message
    if len(myMusic) == 0:
        return render_template('my-music.html',all_music =myMusic, 
        noMusic=True, title='My Music')
    return render_template('my-music.html', all_music =myMusic, 
    title='My Music')

@app.route('/music/<int:mid>/')
def musicItem(mid):
    """ displays the detailed view of one music title and its information """
    if notLoggedIn(): 
        return redirect( url_for('index'))
    # grab music information from database
    conn = dbi.connect()
    musicTitle = music.getSingleMusicTitle(conn, mid)
    userInfo = db_calls.getUserInfo(conn, musicTitle['user_id'])
    # if the user that added item does not exist omits the added by info
    if userInfo is not None:
        return render_template('music-item.html', title=musicTitle['title'], 
        music=musicTitle, addedInfo=True, user=userInfo['username'])
    else: 
        return render_template('music-item.html', title=musicTitle['title'], 
        music=musicTitle, addedInfo=False)

def renderArtistResults(conn, query):
    """given a query looks for that artist in the database
    and returns the results, be either redirecting to that 
    artist's page, showing an error or listing all artists matching 
    the query"""
    results = music.getArtist(conn, query)
    if len(results) == 0: # no results found, display
        return render_template('search-error.html',type='artists', 
        title='Search error')
    elif (len(results) == 1): # redirects to that music/user/artist page
        return redirect(url_for('artistInfo',  aid= results[0]['aid']))
    else:
        return render_template('list.html', type = 'artists', 
        all_things = results, query= query, title="Artist results")

def renderMusicResults(conn, query):
    """given a query looks for that music title in the database
    and returns the results, be either redirecting to that 
    titles' page, showing an error or listing all music titles matching 
    that query"""
    results = music.getMusicByTitle(conn, query)
    if len(results) == 0: # no results found, display
        return render_template('search-error.html',type='music', title='Search error')
    elif (len(results) == 1): # redirects to that music's page
        return redirect(url_for('musicItem',  mid= results[0]['mid']))
    else:
        return render_template('list.html', type = 'titles', all_things = results, 
        query= query, title= 'Music title results')

@app.route('/query/')
def query_lookup():
    """ processes the search for either a music title or an artist """
    # looks at what type of query artist or music and returns results
    query = request.args.get('query')
    kind = request.args.get('kind')
    conn = dbi.connect()
    if kind == 'artist':
        return renderArtistResults(conn, query)
    else:
        return renderMusicResults(conn, query)

# processes the delete request of a particular music title
@app.route('/delete_music/<int:mid>', methods=['POST'])
def delete_music(mid):
    """
    allows a user to delete a music title that they have added to the music 
    database
    """
    try:
        conn = dbi.connect()
        music.deleteMusic(conn,mid) # delete the user
        return redirect(url_for('my_music'))
    except Exception:
        flash('Failed to delete music')
        return redirect(url_for('musicItem', mid=mid))

@app.route('/update_music/<int:mid>', methods=['GET', 'POST'])
def update_music(mid): 
    """
    allows a user to update a music entry they created
    """

    # checks if user is logged in, if not redirects to welcome page
    if notLoggedIn(): 
        return redirect( url_for('index'))

    conn = dbi.connect()
    musicInfo = music.getSingleMusicTitle(conn, mid)
    if request.method == 'POST':
       
        try:
        # update music info if new data is ok 
            artistName = request.form['artist']
            # checks if a new artist was entered as artist 
            aid = checkArtistStatus(conn, artistName)

            music.updateMusicTitle(conn, mid, request.form['title'],
            aid, request.form['genre'], request.form['description'])
            flash('successfully updated music')
            return redirect(url_for('musicItem', mid=mid))

        except Exception as e:
            flash('Failed to update music')
            print(e)
            return redirect(url_for('musicItem', mid=mid))
        
    return render_template('update-music.html',title='Update Profile', 
    music=musicInfo)

@app.route('/artist/<int:aid>')
def artistInfo(aid): 
    """ 
    renders the information page of an artist
    """

    # checks if user is logged in, if not redirects to welcome page
    if notLoggedIn(): 
        return redirect( url_for('index'))

    # gets artist info and displays it
    conn = dbi.connect() 
    artist = music.getArtistById(conn, aid)
    artistsWork = music.getMusicByArtistId(conn, aid)
    return render_template('artist-info.html',title='Artist Info', 
    artist = artist, works = artistsWork)

@app.route('/all_artists/')
def all_artists():
    # checks if user is logged in, if not redirects to welcome page
    if notLoggedIn(): 
        return redirect( url_for('index'))
    
    try:
        conn = dbi.connect()
        allArtists = music.getArtists(conn)
        print('all artists', allArtists)
        return render_template('all-artists.html',title='All Artists', 
        all_artists=allArtists )

    except Exception:
        flash('Failed to display all artists')
        return redirect(url_for('home'))

@app.route('/artist_lookup/')
def artist_lookup():  
    query = request.args.get('query')
    conn = dbi.connect()
    # extract artists from db that match query 
    return renderArtistResults(conn, query)

######## fetching current artists ############
@app.route('/getdata/')
def data_get():
    """ used to get all the artist to create a dynamic way to enter
    artist name when adding/updating music"""
    conn = dbi.connect()
    allArtists = music.getArtists(conn)
    allArtistList = [artist['name'] for artist in allArtists]
    return jsonify({'artists':  allArtistList})
