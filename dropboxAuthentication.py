import base64
import requests

def refresh_dropbox_access_token(app_key, app_secret, refresh_token):
    token_url = "https://api.dropboxapi.com/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + base64.b64encode(f"{app_key}:{app_secret}".encode()).decode(),
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()  # Ensure we got a 2xx response

    return response.json()['access_token']