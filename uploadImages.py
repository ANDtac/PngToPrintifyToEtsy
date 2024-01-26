import requests
from etsyAuthentication import get_etsy_access_token, get_etsy_client_id
from downloadImages import download_images
from getListingImages import get_listing_image_ids
from deleteListingImages import delete_listing_images
import os

def upload_images(listing_id, image_urls):
    # Define headers
    headers = {
        'Authorization': 'Bearer ' + get_etsy_access_token(),
        'x-api-key': get_etsy_client_id(),
    }

    # Get existing images
    existing_image_ids = get_listing_image_ids(listing_id)
    # Delete existing images
    delete_listing_images(listing_id, existing_image_ids)

    # Download the images
    image_paths = download_images(image_urls)

    # Upload new images
    for i, image_path in enumerate(image_paths, 1):
        # Define the upload URL
        upload_url = f'https://openapi.etsy.com/v3/application/shops/SHOPID/listings/{listing_id}/images'

        # Prepare multipart/form-data request
        with open(image_path, 'rb') as image_file:
            files = {
                'image': (os.path.basename(image_path), image_file, 'image/jpeg'),
                'rank': (None, str(i)),
                'overwrite': (None, 'true'),
            }

            # Make the request
            response = requests.post(upload_url, headers=headers, files=files)
            if response.status_code != 201:
                print("Error uploading image:", response.text)
