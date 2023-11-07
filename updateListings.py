from tqdm import tqdm
import json
from etsyAuthentication import get_etsy_access_token, get_etsy_client_id
import requests
from uploadImages import upload_images
import sys
import pandas as pd
from setVariationImages import set_variation_images

def update_listings(grouped_data, listings_json_draft, listings_json_active):
    update_listing_headers = {
        'Authorization': 'Bearer ' + get_etsy_access_token(),
        'x-api-key': get_etsy_client_id(),
        'Content-Type': 'application/json',
    }
    # Initialize the progress bar outside of the loop
    with tqdm(total=len(grouped_data), ncols=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}', leave=False) as pbar:
        # Loop through each group in the grouped data
        for parent_sku, group in grouped_data:
            # Extract the data for the current row
            row = group.iloc[0]
            
            # Update the progress bar and print the current file being uploaded
            pbar.set_description(f"Updating the listing named: {row['title']}")
            sku = row['sku']
            
            temp_id=''
            # Loop through all listings
            for listing in listings_json_draft['results']:
                # Loop through all products in the listing's inventory
                for sku in listing['skus']:
                    # If the product SKU matches your SKU, print the listing ID
                    if sku == row['sku']:
                        temp_id = listing['listing_id']

            for listing in listings_json_active['results']:
                # Loop through all products in the listing's inventory
                for sku in listing['skus']:
                    # If the product SKU matches your SKU, print the listing ID
                    if sku == row['sku']:
                        temp_id = listing['listing_id']

            # List all tags
            all_tags = [str(row[f'tag_{i}']) for i in range(1, 14)]

            # Remove empty strings
            tags = [tag for tag in all_tags if tag]

            new_listing_params = {
                'listing_id': temp_id,
                'parent_sku': str(row['parent_sku']),
                'sku': str(row['sku']),
                'title': str(row['title']),
                'description': str(row['description']),
                'price': str(row['price']),
                'quantity': str(row['quantity']),
                'taxonomy_id': str(row['taxonomy_id']),
                '_primary_color': str(row['_primary_color']),
                '_secondary_color': str(row['_secondary_color']),
                '_occasion': str(row['_occasion']),
                '_holiday': str(row['_holiday']),
                '_diameter': str(row['_diameter']),
                '_dimensions': str(row['_dimensions']),
                '_fabric': str(row['_fabric']),
                '_finish': str(row['_finish']),
                '_flavor': str(row['_flavor']),
                '_height': str(row['_height']),
                '_length': str(row['_length']),
                '_material': str(row['_material']),
                '_pattern': str(row['_pattern']),
                '_scent': str(row['_scent']),
                '_teeshirtsize': str(row['_teeshirtsize']),
                '_style': str(row['_style']),
                '_weight': str(row['_weight']),
                '_width': str(row['_width']),
                '_device': str(row['_device']),
                'option1_name': str(row['option1_name']),
                'option1_value': str(row['option1_value']),
                'option2_name': str(row['option2_name']),
                'option2_value': str(row['option2_value']),
                'image_url': str(row['image_url']),
                'image_position': str(row['image_position']),
                'image_for_option': str(row['image_for_option']),
                'image_1': str(row['image_1']),
                'image_2': str(row['image_2']),
                'image_3': str(row['image_3']),
                'image_4': str(row['image_4']),
                'image_5': str(row['image_5']),
                'image_6': str(row['image_6']),
                'image_7': str(row['image_7']),
                'image_8': str(row['image_8']),
                'image_9': str(row['image_9']),
                'image_10': str(row['image_10']),
                'video_1': str(row['video_1']),
                'length': str(row['length']),
                'width': str(row['width']),
                'height': str(row['height']),
                'dimensions_unit': str(row['dimensions_unit']),
                'weight': str(row['weight']),
                'weight_unit': str(row['weight_unit']),
                'shipping_profile_id': str(row['shipping_profile_id']),
                'processing_min': row['processing_min'],
                'processing_max': row['processing_max'],
                'type': str(row['type']),
                'shop_section_id': str(row['shop_section_id']),
                'who_made': str(row['who_made']),
                'is_made_to_order': str(row['is_made_to_order']),
                'is_vintage': str(row['is_vintage']),
                'when_made': str(row['when_made']),
                'should_auto_renew': str(row['should_auto_renew']),
                'is_taxable': str(row['is_taxable']),
                'is_supply': str(row['is_supply']),
                'is_customizable': str(row['is_customizable']),
                'is_personalizable': str(row['is_personalizable']),
                'personalization_is_required': str(row['personalization_is_required']),
                'personalization_instructions': str(row['personalization_instructions']),
                'personalization_char_count_max': str(row['personalization_char_count_max']),
                'style': [str(row['style_1']), str(row['style_2'])],
                'tags': tags,
                'materials': [str(row['material_1']), str(row['material_2']), str(row['material_3']), str(row['material_4']), str(row['material_5']), str(row['material_6']), str(row['material_7']), str(row['material_8']), str(row['material_9']), str(row['material_10']), str(row['material_11']), str(row['material_12']), str(row['material_13'])],
                'production_partner_ids': [int(row[key]) for key in ['production_partner_1', 'production_partner_2', 'production_partner_3', 'production_partner_4', 'production_partner_5'] if row[key]],
 
                'action': str(row['action']),
                'return_policy_id': '1160276212567',
                'state': 'active',
                'overwrite_images': str(row['overwrite_images'])
            }

            #Remove columns with no value at all
            new_listing_params = {k: v for k, v in new_listing_params.items() if v and not (isinstance(v, list) and not any(v))}

            for key, value in new_listing_params.items():
                if isinstance(value, list):
                    new_listing_params[key] = [item for item in value if item != 'nan']
            
            try:
                listing_id_toUpdate = new_listing_params['listing_id']
            except KeyError:
                print(f"Error: 'listing_id' not found in new_listing_params. One or more drafts have not been created yet. \nYou may delete those draft listings and start again.")
                sys.exit()

            # At the beginning of the for loop where you are updating each listing
            image_urls = [str(row[f'image_{i}']) for i in range(1, 11)]
            upload_images(listing_id_toUpdate, image_urls)

            set_variation_images(listing_id_toUpdate)

            update_listing_json_data = json.dumps(new_listing_params)

            update_listing_url = 'https://openapi.etsy.com/v3/application/shops/42849661/listings/'+str(listing_id_toUpdate)

            response = requests.patch(update_listing_url, headers=update_listing_headers, data=update_listing_json_data)
            if response.status_code == 200:
                pbar.update(1)
            else:
                print("Error updating listing:", response.text)

            
        pbar.set_description(f'')
        print("\nAll listings updated.")

def update_all_changed_listings(changed_listings):
    update_listing_headers = {
        'Authorization': 'Bearer ' + get_etsy_access_token(),
        'x-api-key': get_etsy_client_id(),
        'Content-Type': 'application/json',
    }
    # Initialize the progress bar outside of the loop
    with tqdm(total=len(changed_listings), ncols=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}', leave=False) as pbar:
        # Loop through each group in the grouped data
        for _, row in changed_listings.iterrows():

            new_listing_params_keys = changed_listings.iloc[0].keys() if not changed_listings.empty else []

            # Update the progress bar and print the current file being uploaded
            pbar.set_description(f"Updating the listing named: {row['title']}")
            
            # Set the correct data types based on API requirements
            # Integer types
            for key in ['listing_id', 'quantity', 'shop_section_id', 'personalization_char_count_max', 
                        'shipping_profile_id', 'taxonomy_id', 'production_partner_1', 'production_partner_2']:
                if key in row and row[key]:
                    row[key] = int(row[key])

            # Float types
            for key in ['item_weight', 'item_length', 'item_width', 'item_height']:
                if key in row and row[key]:
                    row[key] = float(row[key])

            # Define new_listing_params based on keys present in output.json
            new_listing_params = {key: row[key] for key in new_listing_params_keys if key in row}

            #Remove columns with no value at all
            new_listing_params = {k: v for k, v in new_listing_params.items() if v and not (isinstance(v, list) and not any(v))}

            for key, value in new_listing_params.items():
                if isinstance(value, list):
                    new_listing_params[key] = [item for item in value if item != 'nan']
            
            try:
                listing_id_toUpdate = new_listing_params['listing_id']
            except KeyError:
                print(f"Error: 'listing_id' not found in new_listing_params. One or more drafts have not been created yet. \nYou may delete those draft listings and start again.")
                sys.exit()

            update_listing_json_data = json.dumps(new_listing_params)

            update_listing_url = 'https://openapi.etsy.com/v3/application/shops/42849661/listings/'+str(listing_id_toUpdate)

            response = requests.patch(update_listing_url, headers=update_listing_headers, data=update_listing_json_data)
            if response.status_code == 200:
                pbar.update(1)
            else:
                print("Error updating listing:", response.text)

            
        pbar.set_description(f'')
        print("\nAll listings updated.")