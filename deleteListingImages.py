import requests
from etsyAuthentication import get_etsy_access_token, get_etsy_client_id

def delete_listing_images(listing_id, listing_image_ids):
    if listing_image_ids is None:
        print(f"No image IDs for listing {listing_id}. Skipping deletion.")
        return
    
    delete_image_headers = {
        'Authorization': 'Bearer ' + get_etsy_access_token(),
        'x-api-key': get_etsy_client_id(),
    }

    # Delete each image by its ID
    for listing_image_id in listing_image_ids:
        delete_image_url = f'https://openapi.etsy.com/v3/application/shops/SHOPID/listings/{listing_id}/images/{listing_image_id}'
        response = requests.delete(delete_image_url, headers=delete_image_headers)

        #if response.status_code != 204:
        #    print("Error deleting image:", response.text)
