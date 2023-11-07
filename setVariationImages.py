import requests
from etsyAuthentication import get_etsy_access_token, get_etsy_client_id
from getListingImages import get_listing_image_ids
from getListingVariations import get_listing_variations

def set_variation_images(listing_id):
    # Define headers
    headers = {
        'Authorization': 'Bearer ' + get_etsy_access_token(),
        'x-api-key': get_etsy_client_id(),
    }

    # Get existing images
    existing_image_ids = get_listing_image_ids(listing_id)

    variation_image_ids_to_set = [existing_image_ids[0], existing_image_ids[2], existing_image_ids[3], existing_image_ids[4],existing_image_ids[1]]

    # Get listing variations
    variations = get_listing_variations(listing_id)

    # Prepare a list to hold the variation image data
    variation_images = []

    # For each variation
    for i, variation in enumerate(variations):
        # Prepare the variation image data
        variation_images.append({
            'property_id': variation['property_id'],
            'value_id': variation['value_id'],
            'image_id': variation_image_ids_to_set[i],
        })

    # Set the variation images
    variation_image_url = f'https://openapi.etsy.com/v3/application/shops/42849661/listings/{listing_id}/variation-images'
    response = requests.post(variation_image_url, headers=headers, json={'variation_images': variation_images})
    if response.status_code != 200:
        print("Error setting variation images:", response.text)
