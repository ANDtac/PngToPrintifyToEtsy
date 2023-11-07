import os
import pandas as pd
import numpy as np
import json
from dropboxUpload import dropbox_upload
from printifyUpload import printify_upload
from createProducts import create_products
from pullListings import pull_listings
from updateListings import update_listings, update_all_changed_listings
from etsyAuthentication import refresh_etsy_authentication
import sys

def add_missing_placeholders(data):
    # Define the placeholders as per the new_data structure you provided
    placeholders = {
        'digital_file_1': '',
        'digital_file_name_1': '',
        'digital_file_2': '',
        'digital_file_name_2': '',
        'digital_file_3': '',
        'digital_file_name_3': '',
        'digital_file_4': '',
        'digital_file_name_4': '',
        'digital_file_5': '',
        'digital_file_name_5': '',
        'style_1': '',
        'style_2': '',
        'production_partner_1': '2958232',
        'production_partner_2': '',
        'production_partner_3': '',
        'production_partner_4': '',
        'production_partner_5': ''
    }
    
    # Loop through each listing in data and add missing placeholders
    for listing in data:
        for key, value in placeholders.items():
            if key not in listing:
                listing[key] = value
    return data

def getPNGs():
    image_files = []
    for root, dirs, files in os.walk('Pictures'):
        for file in files:
            if file.endswith(".png"):
                image_files.append((os.path.join(root, file), os.path.basename(root)))
    return image_files

def create_new_listings():
    if os.path.exists('output.json'):
        decision = input("This option requires deleting output.json. Are you sure? (yes/no): ").strip().lower()
        if decision not in ['y', 'yes']:
            print("Returning to main menu...")
            return
        os.remove('output.json')
    
    # Continue with the previous logic
    # Get a list of all image files in the folder and its subdirectories
    image_files = getPNGs()
    image_urls = dropbox_upload(image_files)
    image_ids = printify_upload(image_urls, image_files)

    products_df = create_products(image_ids, image_files)

    # Save the DataFrame to a JSON file
    products_df.to_json('output.json', orient='records', lines=False)
    print('Listing data saved to output.json successfully.')
    input("Press the Enter key to continue after drafts have appeared on Etsy. Please run menu option 2 after returning to main menu.")


def update_listings_after_creation():
    # Refresh Etsy Authentication
    refresh_etsy_authentication()

    # Read the data from the spreadsheet into a Pandas DataFrame
    spreadsheet_path = 'output.json'
    listing_data = pd.read_json(spreadsheet_path, dtype={'sku': 'str'})

    # Fill NaN values with null
    listing_data = listing_data.fillna(value=np.nan)

    # Group the DataFrame by parent sku
    grouped_data = listing_data.groupby('parent_sku')

    listings_json_draft = pull_listings('draft')
    listings_json_active = pull_listings('active')

    print(f'Updating {len(grouped_data)} listings on Etsy')
    update_listings(grouped_data, listings_json_draft, listings_json_active)
    input("Press Enter to return to the main menu...")



def create_output_json():
    if os.path.exists('output.json'):
        decision = input("This option requires deleting output.json. Are you sure? (yes/no): ").strip().lower()
        if decision not in ['y', 'yes']:
            print("Returning to main menu...")
            return
        os.remove('output.json')
    
    refresh_etsy_authentication()

    # Continue with the previous logic
    listings_json_active = pull_listings('active')
    
    # Extract the 'results' from the response
    listings = listings_json_active.get('results', [])

    # List of allowed keys
    allowed_keys = [
        'listing_id', 'parent_sku', 'sku', 'title', 'description', 'price',
        'quantity', 'taxonomy_id', '_primary_color', '_secondary_color', '_occasion',
        '_holiday', '_diameter', '_dimensions', '_fabric', '_finish', '_flavor',
        '_height', '_length', '_material', '_pattern', '_scent', '_teeshirtsize',
        '_style', '_weight', '_width', '_device', 'option1_name', 'option1_value',
        'option2_name', 'option2_value', 'image_url', 'image_position',
        'image_for_option', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5',
        'image_6', 'image_7', 'image_8', 'image_9', 'image_10', 'video_1', 'length',
        'width', 'height', 'dimensions_unit', 'weight', 'weight_unit',
        'shipping_profile_id', 'processing_min', 'processing_max', 'type',
        'shop_section_id', 'is_made_to_order', 'is_vintage',
        'should_auto_renew', 'is_taxable', 'is_supply', 'is_customizable',
        'is_personalizable', 'personalization_is_required',
        'personalization_instructions', 'personalization_char_count_max', 'style',
        'tags', 'materials', 'production_partner_ids', 'action', 'return_policy_id',
        'state', 'overwrite_images'
    ]

    # Filter the listings to only keep the allowed keys
    filtered_listings = []
    for listing in listings:
        filtered_listing = {key: value for key, value in listing.items() if key in allowed_keys}
        filtered_listings.append(filtered_listing)

    data = add_missing_placeholders(filtered_listings)

    # Save the data back to output.json and outputComparison.json
    with open('output.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    with open('outputComparison.json', 'w') as f:
        json.dump(data, f, indent=4)

    print('Active listings saved to output.json and outputComparison.json successfully.')
    input("Press Enter to return to the main menu...")

def update_listings_from_output_json():
    if not os.path.exists('outputComparison.json'):
        print("outputComparison.json does not exist. Cannot proceed.")
        return
    
    with open('output.json', 'r') as f:
        current_data = json.load(f)
    
    with open('outputComparison.json', 'r') as f:
        comparison_data = json.load(f)
    
    # Find listings that have changed
    changed_listings = [listing for listing in current_data if listing not in comparison_data]
    
    if not changed_listings:
        input("No listings have changed. Press enter to exit...")
        return
    
    # Save only changed listings to output.json
    with open('output.json', 'w') as f:
        json.dump(changed_listings, f, indent=4)
    
    decision = input(f"Would you like to update {len(changed_listings)} listings? (yes/no): ").strip().lower()
    if decision not in ['y', 'yes']:
        print("Update canceled. Returning to main menu...")
        return
    
    # Print the changes
    for listing in changed_listings:
        print(listing)
        print('-' * 50)
    
    input("Above are all the listings being changed. Press Enter to continue...")
    
    # Refresh Etsy Authentication
    refresh_etsy_authentication()

    print(f'Updating {len(changed_listings)} listings on Etsy')
    changed_listings = pd.DataFrame(changed_listings)
    update_all_changed_listings(changed_listings)
    input("Press Enter to return to the main menu...")

def exit_program():
    print("Exiting...")
    sys.exit()

# Defining a list of descriptive names for the menu items
menu_descriptions = [
    "Create New Listings",
    "Update Listings After Creation",
    "Generate output.json for Active Listings",
    "Update Listings Based on output.json Changes",
    "Exit Program"
]

def display_menu(menu_items):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\nChoose an option:")
    for k, description in enumerate(menu_descriptions, 1):
        print(k, description)
    print()

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
                
    functions_names = [create_new_listings, update_listings_after_creation, create_output_json, update_listings_from_output_json, exit_program]
    menu_items = dict(enumerate(functions_names, start=1))
    
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        display_menu(menu_items)
        while True:
            try:
                selection = int(input("Please enter your selection number: "))  # Get function key
                if 1 <= selection <= len(functions_names):
                    selected_value = menu_items[selection]  # Gets the function name
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        if selected_value.__name__ == "exit":
            print("Exiting...")
            break
        else:
            selected_value()

# Run the main function
if __name__ == "__main__":
    main()
