import configparser
import random
import string
import re

from flask import Flask, url_for, request, redirect, render_template

from helpers.secrets import Secrets
from helpers.api import API
from helpers.file_saver import FileSaver


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


@app.route('/save')
def save_from_url():
    """
    This url should be called from a bookmarklet.
    The request must have an url query_parameter containing the 500px photo page of the picture we want to download
    :return: redirect to the original 500px photo page
    """

    # Extract the url of the photo page from the url parameter. This parameter is mandatory
    url = request.args.get('url')
    if not url:
        return "You must include an url query parameter, example: " \
               "http://www.app.com/save?url=https%3A%2F%2F500px.com%2Fphoto%2F124318357%2Fpeace-by-antonio-amati"

    # Get image details, get the image url and save it on the disk

    # Check that the url is valid
    url_match = re.match(r"^https://500px.com/photo/(\d+)/*", url)
    if url_match:
        # Extract photo_id from the url
        photo_id = url_match.group(1)
        # Get image details to get the final image url
        photo_details = api.get('photos/{photo_id}?image_size=2048&comments=0'.format(photo_id=photo_id))
        image_url = photo_details.data.get('photo').get('image_url')

        # Create a file saver object to save the image after download
        file_saver = FileSaver(storage_type=config['Application']['storage_type'],
                               disk_storage_path=config['Application']['disk_storage_path'])

        # Save the image from the image's url
        file_saver.save_image_from_url(url=image_url, photo_id=photo_id)

        # Redirect the url the to original 500px page
        return redirect(url)
    else:
        # The 500px photo page is not valid.
        return str(url) + " is not a valid 500px photo page url"


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
