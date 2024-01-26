import requests
from etsyAuthentication import get_etsy_access_token, get_etsy_client_id

# Endpoint for getting all listings from a shop
pull_listings_url = f"https://openapi.etsy.com/v3/application/shops/SHOPNAME/listings"

def pull_listings(state):
    pull_listings_headers = {
        'Authorization': 'Bearer ' + get_etsy_access_token(),
        'x-api-key': str(get_etsy_client_id()),
        'Content-Type': 'application/json',
    }
    limit = 100  # Maximum limit according to API documentation
    offset = 0  # Start from the beginning
    all_listings = []

    while True:
        pull_listings_parameters = {
            'state': state,
            'limit': limit,
            'offset': offset
        }

        # Make the request
        response = requests.get(pull_listings_url, headers=pull_listings_headers, params=pull_listings_parameters)
        response_json = response.json()

        all_listings.extend(response_json['results'])  # Add the results to our list

        # If there are less listings than the limit, we've fetched all listings
        if len(response_json['results']) < limit:
            break

        # Otherwise, increment the offset by the limit for the next request
        offset += limit

    print(f'Found {len(all_listings)} {state} listings on Etsy')
    return {'results': all_listings, 'count': len(all_listings)}
