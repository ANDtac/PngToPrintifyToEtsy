import requests
from etsyAuthentication import get_etsy_access_token, get_etsy_client_id

def get_listing_image_ids(listing_id):
    get_image_headers = {
        'Authorization': 'Bearer ' + get_etsy_access_token(),
        'x-api-key': get_etsy_client_id(),
    }

    get_image_url = f'https://openapi.etsy.com/v3/application/listings/{listing_id}/images'
    response = requests.get(get_image_url, headers=get_image_headers)
    if response.status_code == 200:
        images = response.json().get('results', [])
        if images:
            # Get the image IDs of all images
            image_ids = [img['listing_image_id'] for img in images]
            return image_ids
    else:
        print("Error getting images:", response.text)
