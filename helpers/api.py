from flask_oauthlib.client import OAuth
from flask import Flask, url_for, request, redirect, flash


class API:
    """
    Handle API authentication and request with 500px
    """

    def __init__(self, consumer_key, consumer_secret):
        oauth = OAuth()
        self.api = oauth.remote_app('500px-fav-downloader',
                                    base_url='https://api.500px.com/v1/',
                                    request_token_url='https://api.500px.com/v1/oauth/request_token',
                                    access_token_url='https://api.500px.com/v1/oauth/access_token',
                                    authorize_url='https://api.500px.com/v1/oauth/authorize',
                                    consumer_key=consumer_key,
                                    consumer_secret=consumer_secret
                                    )

        self.oauth_token = None
        self.oauth_token_secret = None

        # Register the function to get the tokens
        self.api.tokengetter(self.get_oauth_token)

    def get_oauth_token(self):
        """
        Return the needed tokens to sign every request
        :return: oauth_token, oauth_token_secret
        """
        return self.oauth_token, self.oauth_token_secret

    def has_oauth_token(self):
        """
        Check that the oauth tokens are set and the API requests can be made
        :return: True if both tokens are set
        """
        return self.oauth_token is not None and self.oauth_token_secret is not None

    def set_oauth_token(self, oauth_token, oauth_token_secret):
        """
        Set both oauth tokens
        :param oauth_token:
        :param oauth_token_secret:
        :return:
        """
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret

    def authorize(self):
        """
        Redirect the user to 500px to let him authorize the application
        :return: flask.redirect object
        """
        callback_url = url_for('oauth_authorized', next=request.args.get('next'))
        return self.api.authorize(callback=callback_url or request.referrer or None)

    def authorized(self):
        """
        Extract the tokens when the app has been authorized
        :return: oauth_token, oauth_token_secret
        """
        response = self.api.authorized_response()

        # If the response is correct, we save the token in the API helper and return them to be able to save
        # them in the secrets file
        self.oauth_token = response['oauth_token']
        self.oauth_token_secret = response['oauth_token_secret']

        return self.oauth_token, self.oauth_token_secret

    def get(self, path):
        """
        Make a get request on the api
        :param path: path of the api call
        :return: request response
        """
        if not self.has_oauth_token():
            raise RuntimeError("User needs to authorize the application")

        return self.api.request(path)
