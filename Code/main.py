from flask import Flask, redirect, render_template, request,flash, url_for, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import matplotlib.pyplot as plt
import matplotlib
# from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, current_user, UserMixin,login_required
from flask_restful import Resource, Api
from datetime import datetime
import pytz
# from threading import Thread
matplotlib.use('Agg')



app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///musicApp.sqlite"
app.config['SECRET_KEY']= "musicApp"
# CORS(app)
api = Api(app)
db=SQLAlchemy(app)
login_manager=LoginManager(app)


def make_static_folder():
    static_image_folder = os.path.join(app.root_path, 'static', 'image')
    static_audio_folder = os.path.join(app.root_path, 'static', 'audio')
    # Ensuring that the 'static/image' and 'static/audio' folder exists
    if not os.path.exists(static_image_folder) or not os.path.exists(static_audio_folder):
        os.makedirs(static_image_folder)
        os.makedirs(static_audio_folder)
# def delete_static_folder():
#     static_image_folder = os.path.join(app.root_path, 'static','image')
#     static_audio_folder = os.path.join(app.root_path, 'static', 'audio')
#     # Check if the 'static' folder exists
#     if os.path.exists(static_image_folder) or os.path.exists(static_audio_folder):
#         # Iterate through all files in the 'static/image' folder
#         for filename in os.listdir(static_image_folder):
#             file_path = os.path.join(static_image_folder, filename)
#             os.remove(file_path)
#         # Iterate through all files in the 'static/audio' folder
#         for filename in os.listdir(static_audio_folder):
#             file_path = os.path.join(static_audio_folder, filename)
#             os.remove(file_path)
def delete_static_folder():
    static_image_folder = os.path.join(app.root_path, 'static', 'image')
    static_audio_folder = os.path.join(app.root_path, 'static', 'audio')

    # Check if the 'static' folder exists
    if os.path.exists(static_image_folder) or os.path.exists(static_audio_folder):
        # Iterate through all files in the 'static/image' folder
        for filename in os.listdir(static_image_folder):
            file_path = os.path.join(static_image_folder, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing file {file_path}: {e}")

        # Iterate on  all files in the 'static/audio' folder
        for filename in os.listdir(static_audio_folder):
            file_path = os.path.join(static_audio_folder, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing file {file_path}: {e}")


def get_current_time():
    tz = pytz.timezone('Asia/Kolkata')  # Indian time zone
    return datetime.now(tz)

def export_image_song(Songs):
    for song in Songs:
        with open(os.path.join(app.config['UPLOAD_AUDIO_FOLDER'], song.song), 'wb') as f:
            f.write(song.song_data)
        with open(os.path.join(app.config['UPLOAD_IMAGE_FOLDER'], song.image), 'wb') as f:
            f.write(song.image_data)

def export_image_song(Songs):
    for song in Songs:
        audio_file_path = os.path.join(app.config['UPLOAD_AUDIO_FOLDER'], song.song)
        image_file_path = os.path.join(app.config['UPLOAD_IMAGE_FOLDER'], song.image)

        # Check if the files already exist
        if not os.path.exists(audio_file_path):
            with open(audio_file_path, 'wb') as f:
                f.write(song.song_data)

        if not os.path.exists(image_file_path):
            with open(image_file_path, 'wb') as f:
                f.write(song.image_data)
def export_song(song):
    audio_file_path = os.path.join(app.config['UPLOAD_AUDIO_FOLDER'], song.song)
    if not os.path.exists(audio_file_path):
            with open(audio_file_path, 'wb') as f:
                f.write(song.song_data)

def export_profiles(albums):
    for album in albums:
        with open(os.path.join(app.config['UPLOAD_IMAGE_FOLDER'], album.image), 'wb') as f:
            f.write(current_user.image_data)

def export_profile(current_user):
    with open(os.path.join(app.config['UPLOAD_IMAGE_FOLDER'], current_user.image), 'wb') as f:
            f.write(current_user.image_data)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

app.secret_key="spotify"
app.config['UPLOAD_IMAGE_FOLDER']='static/image'
app.config['UPLOAD_AUDIO_FOLDER']='static/audio'

ALLOWED_AUDIO_EXTENSIONS = set(['mp3','wav'])
ALLOWED_IMAGE_EXTENSIONS = set(['png','jpg','jpeg','gif'])
def allowed_audio_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS
def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

app.app_context().push()

class SongResourse(Resource):
    @app.route('/api/song/get_by_id/<int:song_id>',methods=['GET'])
    @login_required
    def get(song_id):
        song=Song.query.get(song_id)
        if song:
            current_song={}
            if current_user.user_id > 0:
                current_song['request']=current_user.f_name
            elif current_user.user_id < 0:
                current_song['request_by_user']=current_user.adminname
            current_song['song_id']=song.song_id
            current_song['tags']=song.tags
            current_song['song_name']=song.song_name
            current_song['artist']=song.artist
            current_song['play_count']=song.play_count
            return current_song , 200
        else:
            return {"Massage": "Song Not Found"},404
    
    # @app.route('/api/song/delete_by_id/<int:song_id>',methods=['DELETE'])
    # @login_required
    # def delete(song_id):
    #     if song_id:
    #         if current_user.user_id > 0:
    #             current_song=Song.query.filter_by(ban_status=False,song_id=song_id).first
    #             if current_song and current_song.created_by==current_user.user_id:
    #                 db.session.delete(current_song)
    #                 db.session.commit()
    #                 return {"Massage": 'Song sccussfully deleted'}
    #             else:
    #                 return{"Massage": "You're not owner of this song so operation can't done"}, 403
    #         elif current_user.user_id < 0:
    #             current_song=Song.query.get(song_id)
    #             if current_song:
    #                 db.session.delete(current_song)
    #                 db.session.commit()
    #                 return {"Massage": 'Song sccussfully deleted'}
    #             else:
    #                 return{"Massage": "Song Not Found"}
    #     else:
    #         return {"Massage": "Song_id not Provided Operation can't done"}, 404

    @app.route('/api/song/delete_by_id/<int:id>',methods=['DELETE'])
    def delete(self,id=None):
        current_song=Song.query.get(id)
        if current_song:
            db.session.delete(current_song)
            db.session.commit()
            return {"Massage":"Song deleted Sccussefully"}
        else:
            return {"Massage": "Song Not Found"}


    
api.add_resource(SongResourse, "/api/song/get_by_id/<int:song_id>", "/api/song/delete_by_id/<int:id>")


class Top_Contributers(Resource):
    def get(self):
        contribution_chart(top_contribution(5))
        return send_from_directory('static/image', 'top_contributors_chart.png')   
api.add_resource(Top_Contributers,'/api/top_contributers')

class Top_Played_Songs(Resource):
    def get(self,number=None):
        top_played_songs_chart(most_played_song(number))
        song_list=most_played_song(number)
        songs={}
        for index, song in enumerate(song_list, start=1):
            song_name = song['songName']
            play_count = song['playCount']
            songs[index] = {'name': song_name, 'Play_Count': play_count}
        return {'data':songs, 'file':'http://127.0.0.1:5000/static/image/top_played_songs_chart.png'}, 200
api.add_resource(Top_Played_Songs,'/api/top_played_songs/<int:number>')




class User(db.Model, UserMixin):
    user_id=db.Column(db.Integer(), primary_key=True, nullable = False)
    f_name = db.Column(db.String())
    username = db.Column(db.String(), nullable=False, unique=True)
    mail = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(),nullable = False)
    image = db.Column(db.String())
    image_data = db.Column(db.LargeBinary)
    ban_status = db.Column(db.Boolean, default=False, nullable=False)
    tags = db.Column(db.String())

    def get_id(self):
        return (self.user_id)
    
    
    def isRoleUser():
        if current_user.role == "User":
            return True
        else:
            return False
        
    def isRoleCreator(user_id):
        if User.query.get(user_id).role == 'Creator':
            return True
        else:
            return False
        
    def Role_to_user(user_id):
        if User.isRoleCreator(user_id):
            User.query.get(user_id).role= "User"
        
    def Role_to_creator(user_id):
        if User.isRoleUser(user_id):
            User.query.get(user_id).role = 'Creator'


class Admin(db.Model, UserMixin):
    user_id=db.Column(db.Integer(), primary_key=True,nullable=False)
    adminname=db.Column(db.String(),nullable=False)
    admin_mail=db.Column(db.String(),nullable=False, unique=True)
    admin_pass=db.Column(db.String(),nullable=False)

    def get_id(self):
        return (self.user_id)

class Song(db.Model):
    song_id=db.Column(db.Integer(), primary_key=True, nullable = False)
    song_name=db.Column(db.String())
    song=db.Column(db.String())
    song_data = db.Column(db.LargeBinary)
    image = db.Column(db.String())
    image_data = db.Column(db.LargeBinary)
    genre = db.Column(db.String())
    artist = db.Column(db.String())
    rating = db.Column(db.Integer())
    lyrics = db.Column(db.String())
    play_count= db.Column(db.Integer())
    tags = db.Column(db.String())
    created_by=db.Column(db.Integer(),db.ForeignKey('user.user_id'))
    ban_status = db.Column(db.Boolean(), default=False, nullable=False)
    uploadtime = db.Column(db.DateTime(),default=datetime.utcnow)

    def addCount(song_id):
        Song.query.get(song_id).play_count = Song.query.get(song_id).play_count + 1
        db.session.commit()

class Playlist(db.Model):
    playlist_id=db.Column(db.Integer(), primary_key=True,nullable=False)
    playlist_name=db.Column(db.String())
    created_by=db.Column(db.Integer(), db.ForeignKey('user.user_id'))
    songs = db.relationship('Song',secondary='playlist_song', backref='playlists')

    def delete_playlist(playlist_id):
        current_playlist=Playlist.query.get(playlist_id)
        db.session.delete(current_playlist.songs)
        db.session.delete(current_playlist)
        db.session.commit()

class Playlist_song(db.Model):
    playlist_song_id=db.Column(db.Integer(),primary_key=True, autoincrement=True)
    playlist_id=db.Column(db.Integer(), db.ForeignKey("playlist.playlist_id"))
    song_id=db.Column(db.Integer(),db.ForeignKey("song.song_id"))

class Album(db.Model):
    album_id=db.Column(db.Integer(),primary_key=True)
    album_name=db.Column(db.String())
    album_desc=db.Column(db.String())
    image_data=db.Column(db.LargeBinary)
    image=db.Column(db.String())
    created_by=db.Column(db.Integer(), db.ForeignKey('user.user_id'))
    is_public=db.Column(db.Boolean(), default=False, nullable=False)
    songs = db.relationship('Song',secondary='album_song', backref='albums')

class Album_song(db.Model):
    album_song_id=db.Column(db.Integer(),primary_key=True, autoincrement=True)
    album_id=db.Column(db.Integer(),db.ForeignKey("album.album_id"))
    song_id=db.Column(db.Integer(),db.ForeignKey("song.song_id"))

class Recently_played(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    user_id=db.Column(db.Integer(), db.ForeignKey('user.user_id'))
    song_id=db.Column(db.Integer(), db.ForeignKey('song.song_id'))
    playtime = db.Column(db.DateTime(),default=datetime.utcnow)

class User_mostplayed(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    user_id=db.Column(db.Integer(), db.ForeignKey('user.user_id'))
    song_id=db.Column(db.Integer(), db.ForeignKey('song.song_id'))
    play_count=db.Column(db.Integer())

@login_manager.user_loader
def load_user(user_id):
    # Check if the user ID corresponds to a regular user or an admin
    user_id = int(user_id)
    if user_id > 0:  # Assuming regular users have IDs greater than 0
        return User.query.get(user_id)
    else:
        return Admin.query.get(user_id)
# def load_user(user_id):
#     return User.query.get(user_id)

def top_contribution(number):
    creator_contribution = []
    all_creators = User.query.filter_by(role='Creator').all()
    for creator in all_creators:
        new_creator = {}
        new_creator['user_id'] = creator.user_id  # Corrected line
        new_creator['songs'] = len(Song.query.filter_by(created_by=creator.user_id).all())
        new_creator['albums'] = len(Album.query.filter_by(created_by=creator.user_id).all())
        new_creator['username'] = creator.username
        creator_contribution.append(new_creator)
    # Sorting the list based on the 'songs' key in descending order
    sorted_creators = sorted(creator_contribution, key=lambda x: x['songs'], reverse=True)
    # Taking the top 'number' contributors
    top_contributors = sorted_creators[:number]
    return top_contributors

def contribution_chart(top_contributors):
    usernames = [contributor['username'] for contributor in top_contributors]
    song_counts = [contributor['songs'] for contributor in top_contributors]
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor('grey')
    ax.set_facecolor('grey')
    # Create a bar chart
    ax.bar(usernames, song_counts, color='orange')
    ax.set_xlabel('Creators')
    ax.set_ylabel('Number of Songs')
    ax.set_title('Top Contributors - Songs Created')
    plt.xticks(rotation=45, ha='right')
    fig.tight_layout()
    save_path = os.path.join('static/image', 'top_contributors_chart.png')
    fig.savefig(save_path)

    plt.close(fig)

def most_played_song(number):
    songs=Song.query.all()
    top_songs=[]
    for song in songs:
        new_song={}
        new_song['song_id']=song.song_id
        new_song['songName']=song.song_name
        new_song['playCount']=song.play_count
        top_songs.append(new_song)

    sorted_top_songs = sorted(top_songs, key=lambda x: x['playCount'], reverse=True)
    top_songs=sorted_top_songs[:number]
    return top_songs

def top_played_songs_chart(top_songs):
    song_names = [song['songName'] for song in top_songs]
    play_counts = [song['playCount'] for song in top_songs]

    # Create a figure
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor('grey')
    ax.set_facecolor('grey')
    ax.bar(song_names, play_counts, color='purple')
    ax.set_xlabel('Songs')
    ax.set_ylabel('Play Count')
    ax.set_title('Top Played Songs')
    ax.set_xticklabels(song_names, rotation=45, ha='right')
    plt.tight_layout()
    save_path = os.path.join('static/image', 'top_played_songs_chart.png')
    plt.savefig(save_path)
    plt.close()


#_____________________________________________________ for registering a new user/creator into the database _______________________________

@app.route('/register_user',methods=['GET','POST'])
def register_user():
    if request.method=="POST":
        mail=request.form.get('mail')
        f_name=request.form.get('name')
        username=request.form.get('username')
        password=request.form.get('password')
        image_data=request.files['image']
        role=request.form.get('role')
        new_username=User.query.filter_by(username=username).first()
        new_mail=User.query.filter_by(mail=mail).first()
        if not new_username and not new_mail:
            new_user=User(mail=mail,f_name=f_name,username=username,password=password,image_data=image_data.read(),role=role)
            db.session.add(new_user)
            db.session.commit()
            filename=str(new_user.username) + 'profile.png'
            new_user.image=filename
            db.session.commit()
            return redirect('/') 
        else:
            massage='this username or email already in use! Try diffrent.'
            
            return render_template('error.html',error=massage) 
    return render_template('register_user.html')

##############################################  LOGIN OF A EXISTING USER AND NOT BANNED BY ADMIN ##########################################

@app.route('/', methods=['GET','POST'])
def login():
    if request.method=='POST':
        credential=request.form.get('username')
        password=request.form.get('password')
        by_mail=User.query.filter_by(username=credential,ban_status=False).first()
        by_username=User.query.filter_by(mail=credential,ban_status=False).first()
        if by_mail:
            if by_mail.password==password:
                login_user(by_mail)
                return redirect('/home')
            else:
                massage="wrong password"
                return render_template('error.html',error=massage)
        elif by_username:
            if by_username.password==password:
                login_user(by_username)
                return redirect('/home')
            else:
                massage="wrong password"
                return render_template('error.html',error=massage)
        else:
            massage="not a user REGISTER YOURSELF"
            link='Register'
            return render_template('error.html',error=massage,link=link)
    return render_template('login.html')


################################# ADMIN LOGIN-------- BUT ALL THE ADMIN CREDENTIALS ONLY CAN REGISTER WHEN DB.CREATE_ALL FUNCTION CALL OR BY TERMINAL 
 

@app.route('/admin_login',methods=['GET','POST'])
def admin_login():
    if request.method=="POST":
        credential=request.form.get('username')
        password=request.form.get('password')
        admin=Admin.query.filter_by(admin_mail=credential).first()
        if admin:
            if admin.admin_pass==password:
                login_user(admin)
                contribution_chart(top_contribution(5))
                top_played_songs_chart(most_played_song(5))
                return redirect('/dashboard')
            else:
                massage="Wrong Password"
                return render_template('error.html',massage=massage)
        else:
            massage='You are not a admin <a href="/login" style="margin-top: 90vh; margin-left:0vw; color: #ea0e0e">login</a>'
            link='Register'
            return render_template('error.html',massage=massage, link=link)
    return render_template('login_admin.html')

##_________________________________USER/CREATOR CAN EDIT OWN PERSON DETAILS eg. NAME, PROFILE PIC, PASSWORD, ROLE ________________________________________####
@app.route('/edit_user',methods=['GET','POST'])
@login_required
def edit_user():
    if request.method=='POST':
        f_name=request.form.get('name')
        password=request.form.get('password')
        image_data=request.files['image']
        current_user.f_name=f_name
        current_user.password=password
        if image_data:
            current_user.image_data=image_data.read()
        db.session.commit()
        return redirect('/home')

    return render_template('edit_user.html',current_user=current_user)

###______THIS ROUTE IS CALLED WHEN THEY CHANGE THIER ROLE TO USER/CREATOR AND IT RETURN TO THE LAST WEB PAGE WITH UPDATED ROLE__________________

@app.route('/change_role', methods=['GET','POST'])
@login_required
def change_role_to_user():
    if current_user.role=="Creator":
        current_user.role="User"
        db.session.commit()
    elif current_user.role=="User":
        current_user.role="Creator"
        db.session.commit()
    return redirect('/edit_user')


#________________________________________ HOME PAGE OF THE USER/CREATOR----that runs some query to respective login_user and return to homepage______

@app.route('/home', methods=['GET','POST'])
@login_required
def home():
    fresh_arrivals=Song.query.filter_by(ban_status=False).order_by(Song.uploadtime.desc()).limit(6).all()
    trending_songs=Song.query.filter_by(ban_status=False).order_by(Song.play_count.desc()).limit(4).all()
    user_mostplayed=User_mostplayed.query.filter_by(user_id=current_user.user_id).order_by(User_mostplayed.play_count.desc()).limit(5).all()
    user_mostplayed_song_id=[]
    for song in user_mostplayed:
        user_mostplayed_song_id.append(song.song_id)
    user_mostplayed_song = db.session.query(Song).filter(Song.song_id.in_(user_mostplayed_song_id),Song.ban_status==False).all()
    user_mostplayed_song = sorted(user_mostplayed_song, key=lambda x: user_mostplayed_song_id.index(x.song_id))
    # user_mostplayed_songs=Song.query.filter_by()
    export_image_song(fresh_arrivals)
    export_profile(current_user)
    songs=Song.query.limit(10).all()
    export_image_song(songs)
    if current_user.role=="User":
        playlists=Playlist.query.filter_by(created_by=current_user.user_id).all()
        return render_template("home1.html",current_user=current_user,fresh_arrivals=fresh_arrivals, user_mostplayed_song=user_mostplayed_song, trending_songs=trending_songs ,playlists=playlists,songs=songs)
    elif current_user.role=="Creator":
        playlists=Playlist.query.filter_by(created_by=current_user.user_id).all()
        return render_template("home1.html",current_user=current_user,fresh_arrivals=fresh_arrivals,user_mostplayed_song=user_mostplayed_song, trending_songs=trending_songs,playlists=playlists,songs=songs)
    
#_______________

@app.route('/get_song_details', methods=['POST'])
def get_song_details():
    song_name = str(request.json.get('songName'))
    song_id=int(song_name[-9])
    current_song=Song.query.get(song_id)
    song = {
        # 'songName' : song_name
        'songName': current_song.song_name, 
        'artistName': current_song.artist,
        # 'albumName': ,
        'genre': current_song.genre,
        'rating':current_song.rating
        # 'duration': '3:30',  # Replace with the actual duration
    }
    return jsonify(song)

#_________________ that function is called by song_play function in javascript and make count of song_play, make user_play_history, and make_user_most_played_song

@app.route('/currently_playing', methods=['POST'])
def currently_playing():
    song_id = int(request.json.get('song_id'))
    user_song=User_mostplayed.query.filter_by(user_id=current_user.user_id,song_id=song_id).first()
    if user_song:
        user_song.play_count+=1
    else:
        user_song=User_mostplayed(user_id=current_user.user_id, song_id=song_id,play_count=1)
        db.session.add(user_song)
    # db.session.commit()
    current_song=Song.query.get(song_id)
    current_song.play_count=current_song.play_count+1
    last=Recently_played.query.filter_by(user_id=current_user.user_id,song_id=song_id).first()
    new=Recently_played(user_id=current_user.user_id,song_id=song_id,playtime=get_current_time())
    if last:
        db.session.delete(last)
        new=Recently_played(user_id=current_user.user_id,song_id=song_id,playtime=get_current_time())
    db.session.add(new)
    db.session.commit()

    
    song_details = {
        'songName': current_song.song_name,
        'artistName': current_song.artist,
        'genre': current_song.genre,
        'rating': current_song.rating,
        'playCount': current_song.play_count,
        'playtime': str(new.playtime)  # Convert playtime to string as needed
    }

    return jsonify(song_details)
    return None

############################################# PLAYLIST SECTION #################################################################

# _____________________________________ CREATING NEW PLAYLIST( you have option to make a empty playlist or add some song)__________________________

@app.route('/create_playlist', methods=['GET','POST'])  
@login_required
def create_playlist():
    all_songs=Song.query.all()
    if request.method=="POST":
        playlist_name=request.form.get('playlist_name')
        selected_songs = request.form.getlist('selected_songs')
        new_playlist=Playlist(playlist_name=playlist_name,created_by=current_user.user_id)
        if selected_songs:
            for song_id in selected_songs:
                new_playlist.songs.append(Song.query.get(song_id))
        db.session.add(new_playlist)
        db.session.commit()
        return redirect('/show_playlist/'+ str(new_playlist.playlist_id))
    return render_template("create_playlist.html",all_songs=all_songs)

# _______________________________DELETE A PLAYLIST_________ALL THE SONGS OF THAT PPLAYLIST WILL DIMINISH_________________________________

@app.route('/delete_playlist/<int:id>')
@login_required
def delete_playlist(id):
    playlist=Playlist.query.get(id)
    if playlist and current_user.user_id == playlist.created_by:
        db.session.delete(playlist)
        db.session.commit()
        return redirect('/home')
    else:
        massage="May be Your are not Owner of this playlist or it may not exists."
        return render_template("error.html",error=massage)


#________________________  VISIT ALL CREATED PLAYLISTS _____________________________________

@app.route('/all_playlists', methods=['GET','POST'])
@login_required
def all_playlists():
    playlist_list=Playlist.query.filter_by(created_by=current_user.user_id).all()
    return render_template('all_playlist.html',playlist_list=playlist_list)





# _____________________________SHOW THE PLAYLIST(BY PASSING PLAYLIST_ID)______ADD/DELETE/PLAY SONGS OF THIS PLAYLIST FORM THIS PAGE_______________

@app.route('/show_playlist/<int:id>', methods=['GET','POST'])
@login_required
def show_playlist(id):
    current_playlist=Playlist.query.get(id)
    if current_playlist.created_by==current_user.user_id:
        playlist_song=current_playlist.songs
        export_image_song(playlist_song)
        return render_template("show_playlist.html",current_playlist=current_playlist,playlist_song=playlist_song,current_user=current_user)
    else:
        massage="May be Your are not Owner of this playlist or it may not exists."
        return render_template("error.html",error=massage)

#______________________________WHEN YOU WANT TO ADD SONG IT GIVE THE OPTIONS OF SONGS TO ADD WHICH ARE NOT IN THIS PLAYLIST______________________

@app.route('/add_song/<int:id>', methods=['GET','POST'])
@login_required
def add_more_song(id):
    current_playlist=Playlist.query.get(id)
    subquery = db.session.query(Playlist_song.song_id).filter_by(playlist_id=id).subquery()
            # Query to find songs that are not in the playlist
    available_song = db.session.query(Song).filter(Song.song_id.notin_(subquery)).all()
    if request.method=='POST':
        selected_songs = request.form.getlist('selected_songs')
        if selected_songs:
            for song_id in selected_songs:
                current_playlist.songs.append(Song.query.get(song_id))
            db.session.commit()
        return redirect('/show_playlist/'+str(current_playlist.playlist_id))
    
    return render_template('add_song.html',current_user=current_user ,current_playlist=current_playlist,available_song=available_song)

#____________________________DELETE SONG FROM PLAYLIST(takes playlist_id,song_id and delete entry from association table)_______________________

@app.route('/delete_song_playlist/<int:p_id>/<int:s_id>')
@login_required
def delete_song_playlist(p_id,s_id):
    current_playlist=Playlist.query.get(p_id)
    if current_playlist.created_by==current_user.user_id:
        song=Playlist_song.query.filter_by(playlist_id=p_id,song_id=s_id).first()
        db.session.delete(song)
        db.session.commit()
        return redirect('/show_playlist/'+str(p_id))
    else:
        return redirect('/home')
#################################################--------END PLAYLIST OPERATIONS-----------------########################################


#----------------------------------------------- ALBUM OPERATIONS ---------------------------------------------
#_____________________________________CREATE A NEW ALBUM(if you are a creator)_____also make private album(just for you)________________________
@app.route('/create_album',methods=['GET','POST'])
@login_required
def create_album():
    if current_user.role=="Creator":
        if request.method=='POST':
            album_name=request.form.get('album_name')
            desc=request.form.get('desc')
            image_data=request.files['image_data']
            privateCheckbox=request.form .get('privateCheckbox')
            if privateCheckbox == 'on':
                privateCheckbox=True
            privateCheckbox=False
            new_album=Album(album_name=album_name,album_desc=desc,image_data=image_data.read(),created_by=current_user.user_id,is_public=privateCheckbox)
            db.session.add(new_album)
            db.session.commit()
            new_album.image=str(new_album.album_id)+'album.png'
            db.session.commit()
            return redirect('/show_album/'+str(new_album.album_id))
        return render_template("create_album.html")
    else:
        massage="you are not a creator so you can't create any album "
        return render_template("error.html",error=massage)

#________________________SHOW THE ALBUM(takes album_id)________if album owner call this method page layout have more funtionalities but 
# _________________________________________________________________________ normal user only see songs and play songs_____________

@app.route('/show_album/<int:id>',methods=['GET','POST'])
@login_required
def show_album(id):
    current_album=Album.query.get(id)
    current_album_songs=current_album.songs
    export_profile (current_album)
    export_image_song(current_album_songs)
    return render_template('show_album.html',current_album=current_album,current_album_songs=current_album_songs)

#  ____________________________________Creator and upload song from thier that automatically will save in database and also album________________
        
@app.route('/song_upload_album/<int:id>',methods=['GET','POST'])
@login_required
def add_song_album(id):
    current_album=Album.query.get(id)
    if current_user.role=="Creator" and current_album.created_by==current_user.user_id:
        if request.method=="POST":
            song_name=request.form.get('song_name')
            artist= request.form.get('artist')
            lyrics=request.form.get('lyrics')
            image_data=request.files['image']
            song_data=request.files['audio']
            genre=request.form.get('genre')
            tags=request.form.get('tags')
            if allowed_audio_file(song_data.filename):
                new_song=Song(song_name=song_name,genre=genre,image_data=image_data.read(),song_data=song_data.read(),lyrics=lyrics,artist=artist,tags=tags,created_by=current_user.user_id,uploadtime=get_current_time())
                db.session.add(new_song)
                db.session.commit()
                new_song.play_count=0
                new_song.song=str(new_song.song_id)+ 'song.mp3'
                new_song.image=str(new_song.song_id)+ 'poster.png'
                db.session.commit()
                id=new_song.song_id
                # new_playlist.songs.append(Song.query.get(song_id))
                current_album.songs.append(Song.query.get(id))
                db.session.commit()
                return redirect('/show_album/'+str(current_album.album_id))
            else:
                massage="Audio filename not allowed! Upload only in .mp3 & .wav"
                return render_template("error.html",error=massage)  
        return render_template("song_upload_album.html",current_album=current_album)
    else:
        massage="May be Your are not Owner of this playlist or it may not exists."
        return render_template("error.html",error=massage)
    

# __________________________________CREATOR CAN DELETE SONG FROM ALBUMS __________________________________________
    
@app.route('/song_delete_album/<int:a_id>/<int:s_id>',methods=['GET','POST'])
@login_required
def song_delete_album(a_id,s_id):
    current_album=Album.query.get(a_id)
    if current_user.user_id==current_album.created_by:
        # song=Song.query.get(s_id)
        deleting_song=Album_song.query.filter_by(album_id=a_id,song_id=s_id).first()
        db.session.delete(deleting_song)
        # db.session.delete(song)
        db.session.commit()
        return redirect('/show_album/'+str(a_id))
    else:
        massage='you are not owner of this album or this song not exists in this album'
        return render_template('error.html',massage=massage)
    
#_________________________________ CREATOR CAN DELETE OWN ALBUM ________(songs corresponding with that album will delete)__________________

@app.route('/delete_album/<int:a_id>', methods=['GET','POST'])
@login_required
def delete_album(a_id):
    current_album=Album.query.get(a_id)
    if current_album and current_album.created_by==current_user.user_id:
        album_song=Album_song.query.filter_by(album_id=a_id).all()
        for song in album_song:
            deleting_song=Song.query.get(song.song_id)
            db.session.delete(deleting_song)
        db.session.delete(current_album)
        db.session.commit()
        return redirect('/all_albums')
    else:
        return redirect('/home')
        

################################### END OF ALBUM OPERATIONS OF CREATORS ########################################
    

################################# SOME MORE THINGS ON CREATORS ##############################################################
# __________________________________CREATOR CAN SEE THIER OVERALL CONTRIBUTION AND SOME INSIGHTS OF HIS/HER UPLOADED SONG_______________________

@app.route('/stats/<int:user_id>', methods=['GET','POST'])
@login_required
def stats(user_id):
    if current_user.user_id >0 and current_user.role=='Creator':
        user_songs=Song.query.filter_by(ban_status=False ,created_by=current_user.user_id).all()
        user_albums=Album.query.filter_by(created_by=current_user.user_id).all()
        export_image_song(user_songs)
        for album in user_albums:
            export_profile(album)
        return render_template('stats.html',user_songs=user_songs,user_albums=user_albums)       
    elif current_user.user_id < 0:
        user_songs=Song.query.filter_by(created_by=user_id).all()
        user_albums=Album.query.filter_by(created_by=user_id).all()
        export_image_song(user_songs)
        for album in user_albums:
            export_profile(album)
        return render_template('stats.html',user_songs=user_songs,user_albums=user_albums)       
    else:
        return redirect('/home')

#################################################   OPERATONS ON SONGS by creator    ###################################
    
#______________________________________ CREATOR UPLOAD SONG IN DATA BASE _________________________________________________________________

@app.route('/song_upload',methods=['GET','POST'])
@login_required
def song_upload():
    if current_user.role=='Creator':
        if request.method=='POST':
            song_name=request.form.get('song_name')
            artist= request.form.get('artist')
            lyrics=request.form.get('lyrics')
            image_data=request.files['image']
            song_data=request.files['audio']
            genre=request.form.get('genre')
            tags=request.form.get('tags')
            if allowed_audio_file(song_data.filename):
                new_song=Song(song_name=song_name,genre=genre,image_data=image_data.read(),song_data=song_data.read(),lyrics=lyrics,artist=artist,tags=tags,created_by=current_user.user_id,uploadtime=get_current_time())
                db.session.add(new_song)
                db.session.commit()
                new_song.play_count=0
                # new_song.tags.append
                new_song.song=str(new_song.song_id)+ 'song.mp3'
                new_song.image=str(new_song.song_id)+ 'poster.png'
                db.session.commit()
                return redirect('/home')
            else:
                massage="Audio filename not allowed! Upload only in .mp3 & .wav"
                return render_template("error.html",error=massage)
        return render_template("song_upload.html")
    massage="you are not a Creator first register as creator"
    return render_template("error.html",error=massage)

#___________________________________ OWNER OF THE SONG EDIT SONG DETAILS _________________________________________________


@app.route('/edit_song/<int:song_id>',methods=['GET','POST'])
@login_required
def edit_song(song_id):
    song=Song.query.get(song_id)
    if request.method=='POST':
        if song and song.created_by==current_user.user_id:
            name=request.form.get('name')
            artist=request.form.get('artist')
            lyrics=request.form.get('lyrics')
            image_data=request.files['image']
            if image_data:
                song.image_data=image_data.read()
            song.song_name=name
            song.artist=artist
            song.lyrics=lyrics
            db.session.commit()
            return redirect('/stats/'+str(current_user.user_id))
        else:
            return redirect('/home')
    return render_template('edit_song.html',song=song)


# ___________________________ OWNER OF THE SONG CAN DELETE HIS/HER SONG_________________________________________

@app.route('/delete_song/<int:song_id>',methods=['GET','POST'])
@login_required
def delete_song(song_id):
    song=Song.query.get(song_id)
    if song.created_by==current_user.user_id:
        db.session.delete(song)
        db.session.commit()
    elif current_user.user_id < 0:
        db.session.delete(song)
        db.session.commit()
    else:
        return redirect('/home')
    return redirect('/stats/'+str(current_user.user_id))
#####################################################    END OF SONG OPERATIONS ###########################################

#__________________________________ fOR VISITNG PLAYED SONG HISTORY(user/creator)_________________________________________________

@app.route('/history',methods=['GET','POST'])
@login_required
def history():
    user_history=Recently_played.query.filter_by(user_id=current_user.user_id).order_by(Recently_played.playtime.desc()).all()
    user_history_songs_ids=[]
    for song in user_history:
        user_history_songs_ids.append(song.song_id)
    user_history_song = db.session.query(Song).filter(Song.song_id.in_(user_history_songs_ids)).all()
    user_history_song = sorted(user_history_song, key=lambda x: user_history_songs_ids.index(x.song_id))
    return render_template('history.html',songs=user_history_song)

#____________________________________  fOR SEARCHING SONG, ALBUM(by tags, desc, name, genre)______________Admin can also search for User/Creator______________

@app.route('/search',methods=['GET','POST'])
@login_required
def search():
    if request.method=="POST":
        value=request.form.get('value')
        songs = Song.query.filter(
        (Song.song_name.ilike(f"%{value}%")) |
        (Song.artist.ilike(f"%{value}%")) |
        (Song.tags.ilike(f"%{value}%")) |
        (Song.genre.ilike(f"%{value}%"))
        ).all()
        export_image_song(songs)
        albums = Album.query.filter(
        (Album.album_name.ilike(f"%{value}%")) |
        (Album.album_desc.ilike(f"%{value}%"))
        ).all()
        for current_album in albums:
            export_profile (current_album)  
        # export_profiles(albums)
        if current_user.user_id < 0:
            users = User.query.filter(
                (User.username.ilike(f"%{value}%")) |
                (User.f_name.ilike(f"%{value}%")) |
                (User.tags.ilike(f"%{value}%"))
                ).all()
            return render_template('search.html',songs=songs,albums=albums,users=users)
        return render_template('search.html',songs=songs,albums=albums)

##########################       ADMIN OPERATIONS   ################################

# ________________________ After the admin login Admin redirect to this Page _________________________________

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if current_user==Admin.query.filter_by(admin_mail=current_user.admin_mail).first():
        all_albums=Album.query.all()
        all_playlists=Playlist.query.all()
        all_songs=Song.query.all()
        all_normal_user=User.query.filter_by(role='User').all()
        all_creator=User.query.filter_by(role='Creator').all()
        return render_template('dashboard.html',all_albums=all_albums,all_playlists=all_playlists,all_songs=all_songs,all_normal_user=all_normal_user,all_creator=all_creator)
    else:
        massage="you are not a admin you are not allowed to do this"
        return render_template('error.html',massage=massage)


#_______________________________ ADMIN VISIT  ALL ALBUMS  ______________________________________

@app.route('/all_albums', methods=['GET','POST'])
@login_required
def all_albums():
    if current_user.role=='Creator':
        album_list=Album.query.filter_by(created_by=current_user.user_id).all()
        for album in album_list:
            export_profile(album)
        return render_template('all_album.html',album_list=album_list)
    else:
        massage='You are a creator This method is not allowed to you'
        return render_template('error.html',massage=massage)

#______________________________  ADMIN VISIT ALL NORMAL USER(irrespective of thier ban_status) ___________________________

@app.route('/all_users',methods=['GET','POST'])
def all_users():
    if current_user==Admin.query.filter_by(admin_mail=current_user.admin_mail).first():
        all_normal_user=User.query.filter_by(role='User').all()
        return render_template('all_things.html',all_normal_user=all_normal_user)

    else:
        massage="you are not a admin you are not allowed to do this"
        return render_template('error.html',massage=massage)
    

# _______________________________ ADMIN CAN VISIT ALL CREATOR AND ALL THIER CONTIBUTIONS ____________________________

@app.route('/all_creators', methods=['GET','POST'])
def all_creators():
    if current_user==Admin.query.filter_by(admin_mail=current_user.admin_mail).first():
        all_creators=User.query.filter_by(role='Creator').all()
        creator_contribution=[]
        for creator in all_creators:
            data={
                'id':creator.user_id,
                'albums': 0,
                'songs': 0
            }
            all_albums=Album.query.filter_by(created_by=creator.user_id).all()
            all_songs=Song.query.filter_by(created_by=creator.user_id).all()
            data['albums']=len(all_albums)
            data['songs']=len(all_songs)
            creator_contribution.append(data)
        return render_template('all_things.html',all_creators=all_creators,creator_contribution=creator_contribution)
    else:
        massage="you are not a admin you are not allowed to do this"
        return render_template('error.html',massage=massage)




#____________________________ ADMIN CAN VISIT ALL SONGS OF DATABASE(irrespective of thier ban_status)_______________________

@app.route("/all_songs",methods=['GET','POST'])
def all_songs():
    if current_user==Admin.query.filter_by(admin_mail=current_user.admin_mail).first():
        all_songs=Song.query.all()
        return render_template("all_song.html",all_songs=all_songs)
    
    else:
        massage="you are not a admin you are not allowed to do this"
        return render_template('error.html',massage=massage)

#____________________________ ADMIN CAN BAN/UNBAN(Song, User, Creator)--------- by sending the object id(id) and object name(what)_________________

@app.route('/ban_unban/<int:id>/<what>', methods=['GET','POST'])
def ban_unban(id,what):
    if current_user==Admin.query.filter_by(admin_mail=current_user.admin_mail).first():
        if what=='User':
            user=User.query.get(id)
            if user.ban_status==True:
                user.ban_status=False
            elif user.ban_status==False:
                user.ban_status=True
            db.session.commit()
            return redirect('/all_users')
        if what=='Creator':
            user=User.query.get(id)
            if user.ban_status==True:
                user.ban_status=False
            elif user.ban_status==False:
                user.ban_status=True
            db.session.commit()
            return redirect('/all_creators')
        elif what=='Song':
            song=Song.query.get(id)
            if song.ban_status==True:
                song.ban_status=False
            elif song.ban_status==False:
                song.ban_status=True
            db.session.commit()
            return redirect('/all_songs')
    else:
        massage="you are not a admin you are not allowed to do this"
        return render_template('error.html',massage=massage)

#_________________________________________lOGOUT(for USER, CREATOR, ADMIN )  delete all songs and poster created on the server side_________________________________________----

@app.route('/logout')
@login_required
def logout():
    logout_user() 
    delete_static_folder()
    return redirect('/')


if __name__=="__main__":
    app.run(debug=True)