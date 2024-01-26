import requests
import webbrowser
import json
import os
import hashlib
import base64
from os import system

# Etsy Authentication details
etsy_client_id = ''
etsy_client_secret = ''
etsy_redirect_uri = 'http://localhost:5000/callback'
scope = 'listings_w listings_r'
authorization_base_url = 'https://www.etsy.com/oauth/connect'
token_url = 'https://api.etsy.com/v3/public/oauth/token'

def generate_code_verifier():
    return os.urandom(40).hex()

def generate_code_challenge(verifier):
    sha256 = hashlib.sha256()
    sha256.update(verifier.encode())
    return base64.urlsafe_b64encode(sha256.digest()).rstrip(b'=').decode()

def generate_refresh_token():
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    state = os.urandom(16).hex()

    # Construct the authorization URL with the code challenge and method
    auth_url = f"{authorization_base_url}?response_type=code&client_id={etsy_client_id}&scope={scope}&redirect_uri={etsy_redirect_uri}&state={state}&code_challenge={code_challenge}&code_challenge_method=S256"
    
    # Open the authorization URL in the user's default browser
    webbrowser.open(auth_url)

    # Login to etsy account and paste http://localhost:5000/callback?code=ANYTHING WITHIN THIS SECTION OF URL&state=
    code = input("Enter the code you obtained from the OAuth2 flow: ")

    data = {
        'grant_type': 'authorization_code',
        'client_id': etsy_client_id,
        'client_secret': etsy_client_secret,
        'redirect_uri': etsy_redirect_uri,
        'code': code,
        'code_verifier': code_verifier
    }

    response = requests.post(token_url, data=data)
    
    if response.status_code == 200 and 'refresh_token' in response.json():
        refresh_token = response.json()['refresh_token']

        # Save refresh token to a Python file
        with open("refresh_token_config.py", "w") as file:
            file.write(f"refresh_token = '{refresh_token}'\n")
            
        print("Refresh token saved to refresh_token_config.py")
    else:
        print("Failed to get refresh token. Response:", response.json())



def main():
    system('cls')
    generate_refresh_token()

if __name__ == "__main__":
    main()
