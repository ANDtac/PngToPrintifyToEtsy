import requests
from refresh_token_config import refresh_token

etsy_client_id = 'h3qbezy1r36z82ol47qpw3dz'
etsy_client_secret = '9oa6uq4ivv'
etsy_refresh_token = refresh_token
etsy_redirect_uri = 'http://localhost:5000/callback'
scope = 'listings_w'
authorization_base_url = 'https://www.etsy.com/oauth/connect'
token_url = 'https://api.etsy.com/v3/public/oauth/token'

def refresh_access_token():
    data = {
        'grant_type': 'refresh_token',
        'client_id': etsy_client_id,
        'client_secret': etsy_client_secret,
        'refresh_token': etsy_refresh_token,
    }
    response = requests.post(token_url, data=data)
    return response.json()

def refresh_etsy_authentication():
    global etsy_access_token
    global etsy_refresh_token
    global expires_in
    refreshed_token_response = refresh_access_token()
    etsy_access_token = refreshed_token_response['access_token']
    etsy_refresh_token = refreshed_token_response['refresh_token']
    expires_in = refreshed_token_response['expires_in']


def get_etsy_access_token():
    return etsy_access_token

def get_etsy_client_id():
    return etsy_client_id