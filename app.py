from flask import Flask, redirect, request, session, url_for, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

# Spotify API credentials (Replace with your credentials)
SPOTIPY_CLIENT_ID = '74f85aa349fb4c3abfb991b1ab8e6fee'
SPOTIPY_CLIENT_SECRET = '666490840cde48c2acfd6ff045ecfda5'
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback'

# Setting up Spotify OAuth
sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, 
                        client_secret=SPOTIPY_CLIENT_SECRET, 
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope='user-library-read playlist-modify-public')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('recommendations'))

@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    token_info = session.get('token_info', None)

    if not token_info:
        return redirect(url_for('login'))

    sp = spotipy.Spotify(auth=token_info['access_token'])

    if request.method == 'POST':
        user_input = request.form['user_input']
        results = sp.search(q=user_input, type='track', limit=40)

        tracks = []
        for item in results['tracks']['items']:
            tracks.append({
                'name': item['name'],
                'artist': item['artists'][0]['name'],
                'album_cover': item['album']['images'][0]['url'],
                'uri': item['uri']  # Track URI
            })

        return render_template('recommendations.html', tracks=tracks)

    return render_template('recommendations.html')

if __name__ == '__main__':
    app.run(debug=True)
