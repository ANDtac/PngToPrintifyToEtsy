import requests
from etsyAuthentication import get_etsy_access_token, get_etsy_client_id

def get_listing_variations(listing_id):
    # Define headers
    headers = {
        'Authorization': 'Bearer ' + get_etsy_access_token(),
        'x-api-key': get_etsy_client_id(),
    }

    # Define the API URL for getting listing inventory
    inventory_url = f'https://openapi.etsy.com/v3/application/listings/{listing_id}/inventory'

    # Make the request
    response = requests.get(inventory_url, headers=headers)
    if response.status_code != 200:
        print("Error getting listing inventory:", response.text)
        print(f"Response status code: {response.status_code}")  # Print the HTTP status code
        return []

    # Parse the response JSON
    inventory = response.json()

    # Prepare a list to hold the product variations
    variations = []

    # Loop through each product in the inventory
    for product in inventory['products']:
        # Loop through each property_value of the product
        for property_value in product['property_values']:
            # Loop through each value_id in the property_values
            for value_id in property_value['value_ids']:
                # Add the variation to the list
                variations.append({
                    'property_id': property_value["property_id"],
                    'value_id': value_id,
                })

    return variations
