#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash


import pymysql.cursors
import bcrypt
salt = bcrypt.gensalt() #generate random salt

from datetime import datetime
now = datetime.now() #get current date and time
date = now.strftime('%Y-%m-%d %H:%M:%S') #format date and time as string

###Initialize the app from Flask
app = Flask(__name__)
app.secret_key = '1234'

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 3306,
                       user='root',
                       password='database',
                       db='FatEar',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def mainpage():
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')


#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    #convert password to bytes using .encode('utf8')
    #then, hash it with salt
    hashedpassword = bcrypt.hashpw(password.encode('utf8'),salt) 
    fname = request.form['fname']
    lastname = request.form['lastname']
    nickname = request.form['nickname']
    
    cursor = conn.cursor() #cursor used to send queries
    
    query = 'SELECT * FROM user WHERE username = %s'
    cursor.execute(query, (username)) #executes query
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO user VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, hashedpassword, fname, lastname, date, nickname))
        conn.commit()
        cursor.close()
        success = "Registration successful! Please login to continue."
        return render_template('register.html', success=success)

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    #cursor used to send queries
    cursor = conn.cursor()

    #get the user's stored password from database
    retrievepwd = 'Select pwd From user Where username = %s'
    cursor.execute(retrievepwd, (username))
    data = cursor.fetchone()
    cursor.close()

    if data is None:
        flash("Username does not exist")
        return redirect(url_for('login'))
    else:
        passwordMatch = False
        try:
            passwordMatch = bcrypt.checkpw(password.encode('utf-8'), data['pwd'].encode('utf-8'))
            if (passwordMatch):
                #creates a session for the the user
                #session is a built in
                session['username'] = username
                return redirect(url_for('home'))
            else:
                flash("Invalid login or username. Try Again")
                return redirect(url_for('login'))
        except (ValueError, TypeError):
            flash("Invalid login. Try Again")
            return redirect(url_for('login'))


@app.route('/searchsong', methods=['GET', 'POST'])
def searchsong():
    
    if request.method == 'POST':
        option = request.form['search_option1']
        searchkeyword = request.form['key']
        cursor = conn.cursor()
        if option == 'artist':
            queryByArtist = ("Select title, fname, lname\
                            From (song natural join artistPerformsSong) join artist using (artistID) \
                            WHERE fname LIKE %s or lname LIKE %s")
            cursor.execute(queryByArtist, ('%'+searchkeyword+'%', '%'+searchkeyword+'%'))
            searchresults = cursor.fetchall()
            cursor.close() 
        elif option == 'genre':
            queryByGenre = ("Select title, fname, lname, genre\
                        From (song natural join songGenre) join artistPerformsSong using (songID) \
                        join artist using (artistID) WHERE genre = %s")
            cursor.execute(queryByGenre, (searchkeyword))
            searchresults = cursor.fetchall()
            cursor.close()
        elif option == 'title':
            queryByTitle = ("Select title, fname, lname\
                            From (song natural join artistPerformsSong) join artist using (artistID) \
                            WHERE title LIKE %s")
            cursor.execute(queryByTitle, ('%'+searchkeyword+'%'))
            searchresults = cursor.fetchall()
            cursor.close()
        elif option == 'albumtitle':
            queryByTitle = ("Select title, fname, lname, albumTitle\
                            From (song natural join songInAlbum) join album using (albumID) \
                            join artistPerformsSong using (songID) \
                            join artist using (artistID) WHERE albumTitle LIKE %s")
            cursor.execute(queryByTitle, ('%'+searchkeyword+'%'))
            searchresults = cursor.fetchall()
            cursor.close()
        elif option == 'rating':
            if searchkeyword.isdigit() and 1 <= int(searchkeyword) <= 5:
                queryByRating = ("Select title, fname, lname, stars\
                                From ((song natural join rateSong) join artistPerformsSong using (songID)) join artist using (artistID) \
                                WHERE stars = %s")
                cursor.execute(queryByRating, (searchkeyword,))
                searchresults = cursor.fetchall()
                cursor.close()
            else:
                flash("Invalid search keyword. Please enter a number between 1 and 5",'error')
                return render_template('searchsong.html')
        else:
            return redirect(url_for('searchsong'))
        
        if searchresults:
            flash(f"Result for {option} '{searchkeyword}'", 'success')
            return render_template('searchsong.html', searchresults = searchresults, keyword=searchkeyword)
        else:
            flash(f"Do not exists {option} with keyword: '{searchkeyword}'", 'error')
            return render_template('searchsong.html')
    
    return render_template('searchsong.html')


@app.route('/songdetails')
def songdetails():
    title = request.args.get('title')
    if title is None:
        message = "<h3 style='font-weight:bold;font-size:1.2em;'>Invalid route. \
            <br><br>Please <a href='/searchsong'>click here</a> to search a song to view song details.\
            <br><br>To go back to the homepage <a href='/'>click here</a>.</h3>"
        return message, 404
    else:
        cursor = conn.cursor()         
        querySong = 'Select songID, title, genre, albumTitle, releaseDate, songURL\
                    From ((song natural join songGenre) join songInAlbum using(songID)) join album using (albumID)\
                    Where title = %s'
        cursor.execute(querySong, (title,))
        songData = cursor.fetchone()

        queryArtist = 'Select fname, lname, artistBio, artistURL\
                        From (artist as A natural join artistPerformsSong) join Song using (songID)\
                        Where title = %s'
        cursor.execute(queryArtist, (title,))
        artistData = cursor.fetchone()

        #query to retrieve review
        queryReview = 'Select reviewText, reviewDate From song natural join reviewSong Where title = %s'
        cursor.execute(queryReview, (title,))
        reviewData = cursor.fetchall()

        queryAvgRating = 'Select title, sum(stars)/count(title) as AvgRating \
                        From rateSong natural join song \
                        Group by title\
                        Having title = %s'
        cursor.execute(queryAvgRating, (title,))
        avgratingData = cursor.fetchone()
        if avgratingData == None:
            avgRating = avgratingData
        else:
            avgRating = avgratingData['AvgRating']

        strtitle = str(title)
        queryPlay = 'Select songURL From song Where title = %s'
        cursor.execute(queryPlay,(strtitle,)) #add commna to make sure it's passes as a tuple
        songurl = cursor.fetchone()
        songurl_string= songurl['songURL']  # extract songurl string from the dictionary
        trackid = songurl_string.split('/')[-1] #[-1] to access the last element from the split

        cursor.close()
        return render_template('songdetails.html', avgrating = avgRating, songData=songData, artistDetails=artistData, 
                            reviews=reviewData, title=title, songurl=songurl, trackid=trackid)

#Rate a Song
@app.route('/submitrating', methods=['GET', 'POST'])
def submitrating():
    if 'username' not in session:
        message = 'This page is protected. It can only be accessed by logged-in users.<a href="/songdetails">Back to Song Details</a>'
        return '<h3 style="font-size: 1.5em;">{}</h3>'.format(message)
    else:
        user = session['username']
        songID = request.form.get('songID')
        title = request.form.get('title')
        ratedstars = request.form.get('ratedstars')
        cursor = conn.cursor()

        #check whether user already submit rating or not
        checkrating = 'Select * From rateSong Where username = %s and songID = %s'
        cursor.execute(checkrating, (user, songID))
        ratingexist = cursor.fetchone()

        if ratingexist:
            flash(f"You have already rated {ratingexist['stars']} stars on this song.")
            return render_template('display.html', title=title)
        else:
            insertNewRating = 'INSERT INTO rateSong VALUES (%s, %s, %s, %s)'
            cursor.execute(insertNewRating, (user, songID , ratedstars, date))
            conn.commit()
            cursor.close()
            flash(f"Successfully rated on this song.")
            return render_template('display.html', title=title)

#Post Review of a song
@app.route('/submitreview', methods=['POST'])
def submitreview():
    if 'username' not in session:
        message = 'This page is protected. It can only be accessed by logged-in users.<a href="/songdetails">Back to Song Details</a>'
        return '<h3 style="font-size: 1.5em;">{}</h3>'.format(message)
    else:
        user = session['username']
        songID = request.form.get('songID')
        title = request.form.get('title')
        reviewtext = request.form.get('reviewtext')
        cursor = conn.cursor()

        #check whether user already submit review or not
        checkreview = 'Select * From reviewSong Where username = %s and songID = %s'
        cursor.execute(checkreview, (user, songID))
        reviewexist = cursor.fetchone()

        if reviewexist:
            flash(f"You have already reviewed this song. \
                You cannot review this song again. Sorry for any inconvience.")
            return render_template('display.html', title=title)
        else:
            insertNewReview = 'INSERT INTO reviewSong VALUES (%s, %s, %s, %s)'
            cursor.execute(insertNewReview, (user, songID , reviewtext, date))
            conn.commit()
            cursor.close()
            flash(f"Successfully reviewed this song.")
            return render_template('display.html', title=title)


@app.route('/home')
def home():
    if 'username' not in session:
        message = 'This page is protected. It can only be accessed by logged-in users.\
                    <br> <br> Go back to the <a href="/">home</a> page.'
        return '<h3 style="font-size: 1.5em;">{}</h3>'.format(message)
    else:
        user = session['username']
        cursor = conn.cursor()

        queryProfile = 'SELECT fname, lname, nickname, lastlogin From user WHERE username = %s'
        cursor.execute(queryProfile, (user))
        userData = cursor.fetchone()

        queryRating = 'Select title, ratingDate, stars From song natural join rateSong Where username = %s Order By ratingDate Desc'
        cursor.execute(queryRating, (user))
        ratingData = cursor.fetchall()

        queryReview = 'Select title, reviewText, reviewDate From song natural join reviewSong Where username = %s Order By reviewDate Desc'
        cursor.execute(queryReview, (user))
        reviewData = cursor.fetchall()

        queryArtistFans = 'Select fname, lname From artist natural join userFanOfArtist Where username = %s'
        cursor.execute(queryArtistFans, (user))
        fansData = cursor.fetchall()

        queryFansNewSongs = 'Select artistID, fname, lname, title, releaseDate, songURL \
                            From (song natural join artistPerformsSong) join artist using (artistID) \
                            Where artistID IN (Select artistID From userFanOfArtist Where username = %s)\
                            And releaseDate > (Select lastlogin From user Where username = %s) Order By releaseDate Desc'
        cursor.execute(queryFansNewSongs, (user, user))
        fansNewSongsData = cursor.fetchall()

        #query user's friends
        queryFriendsList = 'Select FriendName \
                        From ((Select user2 as UserName, user1 as FriendName from friend where acceptStatus = "Accepted")\
                        union\
                        (Select user1 as UserName, user2 as FriendName from friend where acceptStatus = "Accepted")) as Friendship\
                        Where username = %s'
        cursor.execute(queryFriendsList, (user))
        friendslistData = cursor.fetchall()
        
        queryFriRequest = 'Select newrequest\
                            From ((Select user2 as username, user1 as newrequest \
                                    from friend where acceptStatus = "Pending" and requestSentBy != user2) \
                                    union \
                                    (Select user1 as username, user2 as newrequest \
                                    from friend where acceptStatus = "Pending" and requestSentBy != user1)) \
                            as PendingRequest \
                            Where PendingRequest.username = %s '
        cursor.execute(queryFriRequest, (user))
        FriRequestData = cursor.fetchall()
        numRequest = len(FriRequestData)

        #query user's followers
        queryFollowersList = 'SELECT follower From user join follows on user.username = follows.follows \
                            Where username = %s'
        cursor.execute(queryFollowersList, (user))
        followerslistData = cursor.fetchall()
        
        #query following
        queryFollowingList = 'SELECT follows From user join follows on user.username = follows.follower \
                            Where username = %s'
        cursor.execute(queryFollowingList, (user))
        followinglistData = cursor.fetchall() #this give us key: follows and value: friend name

        #retrieve only value: friend name from friendlistData
        friendslist = [f['FriendName'] for f in friendslistData]
        friendslist_str = ",".join([f"'{f}'" for f in friendslist])
        newReviewSongsByFri = None
        #if new reviews by friends exist, query them
        if friendslist_str:
            queryReviewSongsByFris = f"(SELECT title, username, reviewText, reviewDate \
                                    FROM song natural join reviewSong \
                                    WHERE reviewDate > (Select lastlogin from user Where username = %s) \
                                    {'AND username IN ({})'.format(friendslist_str) if friendslist_str else ''} Order By reviewDate Desc)"
            cursor.execute(queryReviewSongsByFris, (user,))
            newReviewSongsByFri = cursor.fetchall()

        followerslist = [f['follower'] for f in followerslistData]
        followerslist_str = ",".join([f"'{f}'" for f in followerslist])
        newReviewSongsByFollowers = None
        #if new reviews by followers exist, query them
        if followerslist_str:
            queryReviewSongsByFollowers = f"(SELECT title, username, reviewText, reviewDate \
                                    FROM song natural join reviewSong \
                                    WHERE reviewDate > (Select lastlogin from user Where username = %s) \
                                    And username IN ({followerslist_str}) Order By reviewDate Desc)"
            cursor.execute(queryReviewSongsByFollowers, (user,))
            newReviewSongsByFollowers = cursor.fetchall()

        #retrieve following list
        followinglist = [f['follows'] for f in followinglistData]
        followinglist_str = ",".join([f"'{f}'" for f in followinglist])
        newReviewSongsByFollowing = None
        #if new reviews by following exist, query them
        if followinglist_str:
            queryReviewSongsByFollowing = f"(SELECT title, username, reviewText, reviewDate \
                                    FROM song natural join reviewSong \
                                    WHERE reviewDate > (Select lastlogin from user Where username = %s) \
                                    And username IN ({followinglist_str}) Order By reviewDate Desc)"
            cursor.execute(queryReviewSongsByFollowing, (user,))
            newReviewSongsByFollowing = cursor.fetchall()

    
        cursor.close()
        return render_template('home.html', username=user, userprofile=userData, fans=fansData, newsongs = fansNewSongsData,
                            ratings=ratingData, reviews=reviewData, friends=friendslistData, countfrirequest= numRequest,
                            followers=followerslistData, following=followinglistData, frirequest=FriRequestData,
                            newsreviewsbyfri=newReviewSongsByFri if newReviewSongsByFri else None,
                            newsreviewsbyfollower=newReviewSongsByFollowers if newReviewSongsByFollowers else None, 
                            newsreviewsbyfollowing=newReviewSongsByFollowing if newReviewSongsByFollowing else None)

#Respond friend request: accept or reject
@app.route('/acceptrequest', methods=['POST'])
def acceptrequest():
    if 'username' not in session:
        message = 'This page is protected. It can only be accessed by logged-in users.\
                    <br> <br> Go back to the <a href="/">home</a> page.'
        return '<h3 style="font-size: 1.5em;">{}</h3>'.format(message)
    else:
        user = session['username']
        sender = request.form['sender']
        response = request.form['response']
        cursor = conn.cursor()

        if response == 'accept':
            query = 'UPDATE friend SET acceptStatus = %s, updatedAt = %s \
                    WHERE requestSentBy = %s And (user1 = %s OR user2 = %s)'
            cursor.execute(query, ('Accepted', date, sender, user, user))
        conn.commit()
        cursor.close()
        return redirect('/home')

#Respond friend request: reject
@app.route('/rejectrequest', methods=['POST'])
def rejectrequest():
    if 'username' not in session:
        message = 'This page is protected. It can only be accessed by logged-in users.\
                    <br> <br> Go back to the <a href="/">home</a> page.'
        return '<h3 style="font-size: 1.5em;">{}</h3>'.format(message)
    else:
        user = session['username']
        sender = request.form['sender']
        response = request.form['response']
        cursor = conn.cursor()

        if response == 'reject':
            query = 'UPDATE friend SET acceptStatus = %s, updatedAt = %s \
                    WHERE requestSentBy = %s And (user1 = %s OR user2 = %s)'
            cursor.execute(query, ('Not accepted', date, sender, user, user))
        conn.commit()
        cursor.close()
        return redirect('/home')

@app.route('/friendprofile')
def friendprofile():
    if 'username' not in session:
        message = 'This page is protected. It can only be accessed by logged-in users.'
        return '<h3 style="font-size: 1.5em;">{}</h3>'.format(message)
    else:
        username = session['username'] #retrieve username from dictionary
        friendname = request.args.get('friendname')
        if friendname is None:
            message = "<h3 style='font-weight:bold;font-size:1.2em;'>Invalid route. Please <a href='/'>click here</a> to go back to the homepage.</h3>"
            return message, 404
        else:
            cursor = conn.cursor()

            queryProfile = 'SELECT fname, lname, nickname, lastlogin From user WHERE username = %s'
            cursor.execute(queryProfile, (friendname))
            userData = cursor.fetchone()

            queryRating = 'Select title, ratingDate, stars From song natural join rateSong Where username = %s'
            cursor.execute(queryRating, (friendname))
            ratingData = cursor.fetchall()

            queryReview = 'Select title, reviewText, reviewDate From song natural join reviewSong Where username = %s'
            cursor.execute(queryReview, (friendname))
            reviewData = cursor.fetchall()

            queryArtistFans = 'Select fname, lname From artist natural join userFanOfArtist Where username = %s'
            cursor.execute(queryArtistFans, (friendname))
            fansData = cursor.fetchall()

            queryFriendsList = 'Select FriendName \
                            From ((Select user2 as UserName, user1 as FriendName from friend where acceptStatus = "Accepted")\
                            union\
                            (Select user1 as UserName, user2 as FriendName from friend where acceptStatus = "Accepted")) as Friendship\
                            Where username = %s'
            cursor.execute(queryFriendsList, (friendname))
            friendslistData = cursor.fetchall()

            queryFollowersList = 'SELECT follower From user join follows on user.username = follows.follows \
                                Where username = %s'
            cursor.execute(queryFollowersList, (friendname))
            followerslistData = cursor.fetchall()
            
            #query following
            queryFollowingList = 'SELECT follows From user join follows on user.username = follows.follower \
                                Where username = %s'
            cursor.execute(queryFollowingList, (friendname))
            followinglistData = cursor.fetchall()

            cursor.close()
            return render_template('friendprofile.html', friendname=friendname,
                                    userprofile=userData, fans=fansData,
                                ratings=ratingData, reviews=reviewData,friends=friendslistData,
                                followers=followerslistData, following=followinglistData)
@app.route('/publicprofile')
def publicprofile():
    if 'username' not in session:
        message = 'This page is protected. It can only be accessed by logged-in users.'
        return '<h3 style="font-size: 1.5em;">{}</h3>'.format(message)
    else:
        username = session['username'] #retrieve username from dictionary
        otheruser = request.args.get('otheruser')
        if otheruser is None:
            message = "<h3 style='font-weight:bold;font-size:1.2em;'>Invalid route. Please <a href='/'>click here</a> to go back to the homepage.</h3>"
            return message, 404
        else:
            cursor = conn.cursor()

            queryProfile = 'SELECT fname, lname, nickname From user WHERE username = %s'
            cursor.execute(queryProfile, (otheruser))
            userData = cursor.fetchone()

            queryRating = 'Select title, ratingDate, stars From song natural join rateSong Where username = %s'
            cursor.execute(queryRating, (otheruser))
            ratingData = cursor.fetchall()

            queryReview = 'Select title, reviewText, reviewDate From song natural join reviewSong Where username = %s'
            cursor.execute(queryReview, (otheruser))
            reviewData = cursor.fetchall()

            queryArtistFans = 'Select fname, lname From artist natural join userFanOfArtist Where username = %s'
            cursor.execute(queryArtistFans, (otheruser))
            fansData = cursor.fetchall()

            cursor.close()
            return render_template('publicprofile.html', otheruser=otheruser,
                                    userprofile=userData, fans=fansData,
                                    ratings=ratingData, reviews=reviewData)
        
#SEARCH USERS
@app.route('/searchusers', methods=['GET', 'POST'])
def searchusers():
    if 'username' not in session:
        message = 'This page is protected. It can only be accessed by logged-in users.'
        return '<h3 style="font-size: 1.5em;">{}</h3>'.format(message)
    else:
        username = session['username'] #retrieve username from dictionary
        if request.method == 'POST':
            name = request.form.get('name')

            cursor = conn.cursor() #create connection

            query_user = "SELECT Distinct username, fname, lname, nickname, lastlogin \
                         FROM user \
                         WHERE (user.username LIKE %s OR user.nickname LIKE %s OR user.fname LIKE %s OR user.lname LIKE %s)\
                         AND user.username != %s"
            cursor.execute(query_user, ('%'+name+'%', '%'+name+'%', '%'+name+'%', '%'+name+'%', username))
            data = cursor.fetchall()
            conn.commit() #commit transaction
            cursor.close() #close the cursor to free up resources
            if data:
                return render_template('searchusers.html', username=name, searchresults=data)
            else:
                flash(f"No user exist with username '{name}' ")
                return render_template('searchusers.html', username=username)
        else:
            return render_template('searchusers.html')
        
@app.route('/addfriend', methods=['POST'])
def addfriend():
    if 'username' not in session:
        message = 'This page is protected. It can only be accessed by logged-in users.'
        return '<h3 style="font-size: 1.5em;">{}</h3>'.format(message)
    else:
        username = session['username']
        receiver = str(request.form['receiver'])  
        cursor = conn.cursor()

        # Check if the two users are already friends
        checkfriendship = "SELECT * \
                            FROM ((Select user2 as username, user1 as receiver, acceptStatus From friend)\
                                    Union \
                                   (Select user1 as username, user2 as receiver, acceptStatus From friend)) as Friendship \
                            WHERE username = %s and receiver = %s"
        cursor.execute(checkfriendship, (username, receiver))
        checkFriendStatus = cursor.fetchone()

        if checkFriendStatus: #if two users are friend
            if checkFriendStatus['acceptStatus'] == 'Accepted':
                flash(f"{receiver} is already your friend!")
            elif checkFriendStatus['acceptStatus'] == 'Pending':
                flash(f"Friend request to {receiver} is already send.")
            elif checkFriendStatus['acceptStatus'] == 'Not accepted':
                flash(f"Cannot send friend request to {receiver} again.")
        else:
            if username.lower() < receiver.lower():
                user1 = username
                user2 = receiver
            elif username.lower() > receiver.lower():
                user1 = receiver
                user2 = username

            requestQuery = 'INSERT INTO friend (user1, user2, acceptStatus, requestSentBy, createdAt, updatedAt) \
                            VALUES (%s, %s, %s, %s, %s, %s)'
            cursor.execute(requestQuery, (user1, user2, 'Pending', username, date, date))
            conn.commit()
            cursor.close()
            flash(f'Friend Request Send Successfully to {receiver}!')
        return redirect(url_for('searchusers'))

@app.route('/follow', methods=['POST'])
def follow():
    if 'username' not in session:
        message = 'This page is protected. It can only be accessed by logged-in users.'
        return '<h3 style="font-size: 1.5em;">{}</h3>'.format(message)
    else:
        username = session['username'] #follower in table
        receiver = str(request.form['receiver']) #follows
        cursor = conn.cursor()

        # Check if the two users are already follows
        checkfollowstatus = "Select * From follows \
                            Where follower = %s And follows = %s"
        cursor.execute(checkfollowstatus, (username, receiver))
        checkFollowStatus = cursor.fetchone()

        if checkFollowStatus: #if user already follows the receiver
            flash(f"You already follows {receiver}")
        else:
            followsQuery = 'INSERT INTO follows (follower, follows, createdAt) \
                            VALUES (%s, %s, %s)'
            cursor.execute(followsQuery, (username, receiver, date))
            conn.commit()
            cursor.close()
            flash(f'Successfully follow {receiver}!')
        return redirect(url_for('searchusers'))

@app.route('/logout')
def logout():
    username = session['username']
    cursor = conn.cursor()
    #update last login
    updatelogin = 'Update user SET lastlogin = %s Where username = %s'
    cursor.execute(updatelogin, (date, username))
    conn.commit()
    cursor.close()
    session.pop('username')
    return redirect('/')

@app.errorhandler(404) 
def invalid_route(e):
    message = "<h3 style='font-weight:bold;font-size:1.5em;'> Invalid route. \
                <br>Please <a href='/'>click here</a> to go back to the Home page.</h3>"
    return message, 404

@app.errorhandler(405)
def method_not_allowed(e):
    message = "<h3 style='font-weight:bold;font-size:1.5em;'> Method not allowed. \
                <br>Please <a href='/'>click here</a> to go back to the Home page.</h3>"
    return message, 405

if __name__ == "__main__":
    app.run('127.0.0.1', 3000, debug = True)

