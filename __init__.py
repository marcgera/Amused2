from flask import Flask, render_template, request, url_for, redirect
from classes.AmusedDB import AmusedDB
import json
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from oauthlib.oauth2 import WebApplicationClient
import requests

import os
import pathlib




import requests
from flask import Flask, session, abort, redirect, request


print('')
print(' **********************************************************')
print(' *                                                        *')
print(' * Amused server - Marc Geraerts - October 2022 - V1.1    *')
print(' *     Institute of Rehabilitation Science - UHasselt     *')
print(' *                                                        *')
print(' **********************************************************')
print('')

# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

db = AmusedDB()
db.create_db()
db.populateDB()

global user_ID
global playlist_ID

app = Flask(__name__)
app.secret_key = "!g$FRrWwkqtCZfrsptyYWwBb*"

app.config["SQLALCHEMY_DATABASE_URI"] = db.get_db_uri()
dba = SQLAlchemy(app)

class User(dba.Model):
    id = dba.Column(dba.Integer, primary_key=True)
    user_name = dba.Column(dba.String(200))
    user_surname = dba.Column(dba.String(200))
    user_email = dba.Column(dba.String(200), nullable=False, unique=True)
    user_password = dba.Column(dba.String(200))

    def __repr__(self):
        return '<Name %r' % self.user_name


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    # Create a user in your db with the information provided
    # by Google

    admin = Admin()
    admin = admin.get_admin(users_email)
    global user_id
    user_id = admin.ID

    # Begin user session by logging the user in
    login_user(admin)

    # Send user back to homepage
    return redirect(url_for("index"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getCategories')
def getCategories():
    return json.dumps(db.getCategories('EN'))

@app.route('/dbDump')
def dbDump():
    return db.dump()

@app.route('/getLevels')
def getLevels():
    return json.dumps(db.getLevels('EN'))

@app.route('/logVideo', methods=['GET'])
def logClip():
    video_ID = int(request.args.get('video_ID'))
    background_ID = int(request.args.get('background_ID'))
    playlist_ID = int(request.args.get('playlist_ID'))
    db.logVideo(video_ID, background_ID, playlist_ID)
    return "http200OK"

@app.route('/logMusic', methods=['GET'])
def logMusic():
    music_ID = int(request.args.get('music_ID'))
    playlist_ID = int(request.args.get('playlist_ID'))
    db.logMusic(music_ID, playlist_ID)
    return "http200OK"


@app.route('/getBackgrounds')
def getBackgrounds():
    return json.dumps(db.getBackgrounds('EN'))

@app.route('/getLogsVideo', methods=['GET'])
def getLogsVideo():
    therapist_ID = int(request.args.get('therapist_ID'))
    result = db.getLogVideo(therapist_ID)
    return '\r\n'.join(result)

@app.route('/getLogsMusic', methods=['GET'])
def getLogsMusic():
    therapist_ID = int(request.args.get('therapist_ID'))
    result = db.getLogMusic(therapist_ID)
    return '\r\n'.join(result)

@app.route('/getVideos', methods=['GET'])
def getVideos():
    categories_SO = int(request.args.get('categories_SO'))
    levels_SO = int(request.args.get('levels_SO'))
    backgrounds_SO = int(request.args.get('backgrounds_SO'))
    return json.dumps(db.getVideos(categories_SO, levels_SO, backgrounds_SO))


@app.route('/getMusic', methods=['GET'])
def getMusic():
    categories_SO = request.args.get('categories_SO')
    return json.dumps(db.getMusic(categories_SO))


@app.route('/therapist', methods=['GET'])
def therapist():
    global user_ID
    user_ID = request.args.get('user_ID')
    return render_template('therapist.html')


@app.route('/playlist', methods=['GET'])
def playlist():
    global playlist_ID
    playlist_ID = request.args.get('playlist_ID')
    return render_template('player.html')


@app.route('/playerMSE', methods=['GET'])
def playerMSE():
    global playlist_ID
    playlist_ID = request.args.get('playlist_ID')
    return render_template('playerMSE.html')


@app.route('/getPlaylists')
def getPlaylists():
    return json.dumps(db.getPlaylists(user_ID))


@app.route('/removeFromPlayList', methods=['GET'])
def removeFromPlayList():
    playlistItem_ID = request.args.get('playlistitem_ID')
    return db.removeFromPlayList(playlistItem_ID)


@app.route('/editPlayListName', methods=['GET'])
def editPlayListName():
    playlist_ID = request.args.get('playlist_ID')
    playlistName = request.args.get('playlist_name')
    return db.editPlayListName(playlist_ID, playlistName)


@app.route('/getPlaylistItems', methods=['GET'])
def getPlaylistItems():
    playlist_ID = request.args.get('playlist_ID')
    return json.dumps(db.getPlaylistItems(playlist_ID))


@app.route('/getPlaylistItemsMusic', methods=['GET'])
def getPlaylistItemsMusic():
    playlist_ID = request.args.get('playlist_ID')
    return json.dumps(db.getPlaylistItemsMusic(playlist_ID))


@app.route('/getPlaylistItemsVideo', methods=['GET'])
def getPlaylistItemsVideo():
    playlist_ID = request.args.get('playlist_ID')
    return json.dumps(db.getPlaylistItemsVideo(playlist_ID))


@app.route('/getPlaylistItems2')
def getPlaylistItems2():
    global playlist_ID
    return json.dumps(db.getPlaylistItems(playlist_ID))


@app.route('/movePlayListItem', methods=['GET'])
def movePlayListItem():
    playlistItem_ID = request.args.get('playlistitem_ID')
    direction = request.args.get('direction')
    tableName = request.args.get('tableName')
    db.movePlaylistitem(playlistItem_ID, tableName, direction)
    return 'http200OK'


@app.route('/add2PlaylistItems', methods=['GET'])
def add2PlaylistItems():
    playlist_ID = request.args.get('playlist_ID')
    video_ID = request.args.get('video_ID')
    music_ID = request.args.get('music_ID')
    db.add2PlaylistItems(playlist_ID, video_ID, music_ID)
    return 'http200OK'


@app.route('/addMusic2PlaylistItems', methods=['GET'])
def addMusic2PlaylistItems():
    playlist_ID = request.args.get('playlist_ID')
    music_ID = request.args.get('music_ID')
    db.addMusic2PlaylistItems(playlist_ID, music_ID)
    return 'http200OK'


@app.route('/addVideo2PlaylistItems', methods=['GET'])
def addVideo2PlaylistItems():
    playlist_ID = request.args.get('playlist_ID')
    video_ID = request.args.get('video_ID')
    db.addVideo2PlaylistItems(playlist_ID, video_ID)
    return 'http200OK'


@app.route('/removeFromPlaylist', methods=['GET'])
def removeFromPlaylist():
    playlist_item_ID = request.args.get('playlist_item_ID')
    table_name = request.args.get('table_name')
    db.removeFromPlayList(playlist_item_ID, table_name)
    return 'http200OK'


@app.route('/addPlaylist', methods=['GET'])
def addPlaylist():
    playlist_name = request.args.get('playlist_name')
    db.addPlayList(user_ID, playlist_name)
    return 'http200OK'


@app.route('/removePlaylist', methods=['GET'])
def removelaylist():
    playlist_ID = request.args.get('playlist_ID')
    db.removePlayList(playlist_ID)
    return 'http200OK'

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=5000, debug=True)
# [END gae_flex_quickstart]
