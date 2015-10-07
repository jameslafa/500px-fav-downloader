import configparser
import random
import string
from flask import Flask, url_for, request, redirect, flash, render_template
from helpers.secrets import Secrets
from helpers.api import API

# Read the config file
config = configparser.ConfigParser()
config.read('config/config.ini')

# Initialize secret files
secrets = Secrets(file_path=config['Secrets']['file_path'])

# Initialize API helper
api = API(consumer_key=config['OAuth']['consumer_key'], consumer_secret=config['OAuth']['consumer_secret'])

# If we already have user tokens, we initialize the API with it
if secrets.has_section('OAuth'):
    api.set_oauth_token(oauth_token=secrets.get('OAuth', 'oauth_token'),
                        oauth_token_secret=secrets.get('OAuth', 'oauth_token_secret'))

# Build the flask application
app = Flask(__name__)


@app.route('/login')
def login():
    """
    Login on 500px to authorize the application
    """
    return api.authorize()


@app.route('/oauth-authorized')
def oauth_authorized():
    """
    Endpoint called by 500px to give the tokens
    We save the tokens in the secrets file to avoid the need to login again
    """
    oauth_token, oauth_token_secret = api.authorized()
    secrets.put('OAuth', 'oauth_token', oauth_token)
    secrets.put('OAuth', 'oauth_token_secret', oauth_token_secret)
    secrets.save_file()

    # We redirect the user to the index page when he is correctly authenticated
    return redirect(url_for('index'))


@app.route('/')
def index():
    try:
        # Build a simple list of user favorite. It's just a prototype
        users_resp = api.get('users')
        user_id = users_resp.data.get('user').get('id')
        favorites_resp = api.get(
            'photos?feature=user_favorites&user_id={user_id}&sort=created_at&image_size=3'.format(user_id=user_id))
        return render_template('index.html', user=users_resp.data['user'], favorites=favorites_resp.data['photos'])
    except RuntimeError:
        # Couldn't request the api, ask the user to login again
        return render_template('login_required.html')


# Run the flask application
if __name__ == "__main__":
    # Set the flask session secret key
    # If it is not in the secrets file, generate a new one and save it in the file
    if secrets.get('Flask_session', 'secret_key'):
        app.secret_key = secrets.get('Flask_session', 'secret_key')
    else:
        app.secret_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        secrets.put('Flask_session', 'secret_key', app.secret_key)
        secrets.save_file()

    # Start flask application
    app.debug = config['Flask'].getboolean('debug')
    app.run()
