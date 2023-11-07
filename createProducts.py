from tqdm import tqdm
import requests
import os
import json
import pandas as pd

printify_base_url = "https://api.printify.com/v1"
printify_api_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6ImQ5ZDU3ZGI4MGZhMmE5YmFlZjVkYThlZTIzMjAwOGEzZTdmMWFmNzBhZTJjYzRlZWM0NzcxZTJlMWE0NTI3ZWY1MDAxNzA3MzhlNTQ3ODQ3IiwiaWF0IjoxNjg0MTY3NTIzLjQ4MjM3MSwibmJmIjoxNjg0MTY3NTIzLjQ4MjM3NCwiZXhwIjoxNzE1Nzg5OTIzLjQ3NzcsInN1YiI6IjExOTI5NzI4Iiwic2NvcGVzIjpbInNob3BzLm1hbmFnZSIsInNob3BzLnJlYWQiLCJjYXRhbG9nLnJlYWQiLCJvcmRlcnMucmVhZCIsIm9yZGVycy53cml0ZSIsInByb2R1Y3RzLnJlYWQiLCJwcm9kdWN0cy53cml0ZSIsIndlYmhvb2tzLnJlYWQiLCJ3ZWJob29rcy53cml0ZSIsInVwbG9hZHMucmVhZCIsInVwbG9hZHMud3JpdGUiLCJwcmludF9wcm92aWRlcnMucmVhZCJdfQ.Aps4lS51TIkbTXQWRCtFoECQ1kEYN1WN8neu9VDvYawNpCeaVhuDIxpCdPovDyfRcpsWpIZ4Z39lCoIN1Fs'


df = pd.read_excel('columns.xlsx', index_col=0)
subfolder_mapping = pd.read_excel('catogory_codes.xlsx')

# Read the description text from file
with open('Description.txt', "r") as f:
    description_text = f.read()

# Read the variant data from the spreadsheet
variant_data_df = pd.read_excel('variants.xlsx', sheet_name=0)

def create_products(image_ids, image_files):
    product_ids = []
    products_df = pd.DataFrame()
    print(f'Creating {len(image_ids)} products')
    # Initialize the progress bar outside of the loop
    with tqdm(total=len(image_ids), ncols=70, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}', leave=False) as pbar:
        # Loop through each image ID and create a product
        for image_id in image_ids:
            pbar.set_description(f"Processing image ID: {image_id}")
            # Set the product title and file name to be the same as the image file name, with subfolder name appended
            file_name = os.path.basename(str(image_files[image_ids.index(image_id)]))
            subfolder_name = image_files[image_ids.index(image_id)][1]
            product_title = os.path.splitext(file_name)[0] + " - " + subfolder_name + " - Canvas Wall Art"

            # Create a list of variants with their prices
            variants = []
            for index, row in variant_data_df.iterrows():
                variant_id = int(row["vid"])
                variant_size = row["size"] 
                variant_scale = row["scale"]
                variant_price = row["price"]
                variants.append(
                    {
                        "id": variant_id,
                        "price": variant_price,
                        "options": [{"value": variant_size}],
                    }
                )
            tags = row["tags"].split(",") + [subfolder_name]

            # Create a print area with the image and variants
            print_areas = [
                {
                    "variant_ids": [variant["id"] for variant in variants],
                    "placeholders": [
                        {
                            "position": "front",
                            "print_on_sides": True,
                            "images": [
                                {
                                    "id": image_id, 
                                    "x": 0.5,
                                    "y": 0.5,
                                    "scale": variant_scale,
                                    "angle": 0,
                                }
                            ],
                        }
                    ],
                }
            ]

            print_details = {"print_on_side": "regular"}

            category_code = subfolder_mapping.loc[subfolder_mapping['Subfolder'] == subfolder_name, 'CategoryCode'].iloc[0]

            # Create the product data
            product_data = {
                "title": product_title,
                "description": f"{product_title}\n\n{description_text}",
                "blueprint_id": 50,
                "print_provider_id": 2,
                "variants": variants,
                "print_areas": print_areas,
                "visible": False,
                "print_details": print_details,
                "tags": tags,
            }

            # Upload the product data to Printify
            headers = {
                "Authorization": f"Bearer {printify_api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Python/3.9 Requests/2.28.2 VisualStudio/17.5.3",
            }
            product_upload_url = printify_base_url + "/shops/8680012/products.json"
            response = requests.post(product_upload_url, headers=headers, json=product_data)

            if response.status_code == 200:
                product_id = response.json()["id"]
                product_ids.append(product_id)


                # Specify payload for the request body
                payload = {
                    "title": True,
                    "description": True,
                    "images": False,
                    "variants": True,
                    "tags": True, 
                    "visible": False,
                    "shipping_template": False
                }

                # Retrieve the created product information and append it to the product_info list
                headers = {
                    "Authorization": f"Bearer {printify_api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Python/3.9 Requests/2.28.2 VisualStudio/17.5.3",
                }
                product_pub_url = f"{printify_base_url}/shops/8680012/products/{product_id}/publish.json"
                response = requests.post(product_pub_url, data=json.dumps(payload), headers=headers)

                # Retrieve the created product information and append it to the product_info list
                headers = {
                    "Authorization": f"Bearer {printify_api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Python/3.9 Requests/2.28.2 VisualStudio/17.5.3",
                }
                product_info_url = f"{printify_base_url}/shops/8680012/products/{product_id}.json"
                response = requests.get(product_info_url, headers=headers)

            

                if response.status_code == 200:
                    product_data = response.json()
                    if 'variants' in product_data:              
                        variants = product_data['variants']
                        enabled_variants = []
                        variant_id_list = []
                        url_dict = {}
                

                        for prod_id in product_ids: 
                            if response.status_code == 200:
                                product_data = response.json()
                                if 'images' in product_data:
                                    images = product_data['images']
                                    if len(images) > 0:
                                        # Extract the image sources from the JSON
                                        image_sources = []
                                        for image in images:
                                            image_sources.append(image['src'])

                                        for image in images:
                                            url = image['src']
                                            url_parts = url.split('/')
                                            product_id = url_parts[-4]
                                            var_id = url_parts[-3]
                                            camera_label = url_parts[-1].split('=')[-1]

                                            url_dict[var_id] = url_dict.get(var_id, {})
                                            url_dict[var_id][camera_label] = url

                        # Now you can use the url_dict to link the URLs to each variant as you loop through them
                        for variant in variants:
                            var_id = str(variant['id'])
                            camera_label = 'side'                                   
                            var_url = url_dict.get(var_id, {}).get(camera_label)                                                                          
                
                        for variant in variants:
                            if variant['is_enabled']:
                                enabled_variants.append(variant)
                                variant_id_list.append(variant['id'])
                        

                        if len(enabled_variants) > 0:
                            product_data['variants'] = enabled_variants
                        


                            # Extract the relevant fields
                            id = product_data['id']
                            title = product_data['title']
                            description = product_data['description']
                            tags = ', '.join(product_data['tags'])
                            sizes = ', '.join([size['title'] for size in product_data['options'][0]['values']])
                            depths = ', '.join([depth['title'] for depth in product_data['options'][1]['values']])

                                                                                    
                                    
                            variants = pd.json_normalize(product_data, record_path=['variants'], meta=['id'], meta_prefix='product_')
                            # Create a new DataFrame for the current product
                            product_df = pd.json_normalize(product_data, record_path=['variants'], meta=['id'], meta_prefix='product_')

                            vid_title = variant_data_df.loc[variant_data_df['vid'] == variants['id'], 'size']

                            variants['price'] = variants['price'].apply(lambda x: "{:.2f}".format(x/100))

                            # Add the data to the DataFrame
                            new_data = pd.DataFrame({
                                'listing_id': '',
                                'parent_sku': id,
                                'sku': variants['sku'],
                                'title': title,
                                'description': description,
                                'price': variants['price'],
                                'quantity': variants['quantity'],
                                'taxonomy_id': '1029',
                                '_primary_color': '',
                                '_secondary_color': '',
                                '_occasion': '',
                                '_holiday': '',
                                '_diameter': '',
                                '_dimensions': '',
                                '_fabric': '',
                                '_finish': '',
                                '_flavor': '',
                                '_height': '',
                                '_length': '',
                                '_material': '',
                                '_pattern': '',
                                '_scent': '',
                                '_teeshirtsize': '',
                                '_style': '',
                                '_weight': '',
                                '_width': '', 
                                '_device': '',
                                'option1_name': 'Size',
                                'option1_value': vid_title,
                                'option2_name': '',
                                'option2_value': '',
                                'image_url': '',
                                'image_position': '',
                                'image_for_option': '',
                                'image_1': url_dict.get(str(variant_data_df.at[0,"vid"]), {}).get('side'), 
                                'image_2': url_dict.get(str(variant_data_df.at[4,"vid"]), {}).get('side'),
                                'image_3': url_dict.get(str(variant_data_df.at[1,"vid"]), {}).get('side'),
                                'image_4': url_dict.get(str(variant_data_df.at[2,"vid"]), {}).get('side'), 
                                'image_5': url_dict.get(str(variant_data_df.at[3,"vid"]), {}).get('side'), 
                                'image_6': url_dict.get(str(variant_data_df.at[0,"vid"]), {}).get('back'),
                                'image_7': url_dict.get(str(variant_data_df.at[1,"vid"]), {}).get('context-4'),
                                'image_8': url_dict.get(str(variant_data_df.at[2,"vid"]), {}).get('context-3'),
                                'image_9': url_dict.get(str(variant_data_df.at[3,"vid"]), {}).get('context-2'),
                                'image_10': url_dict.get(str(variant_data_df.at[4,"vid"]), {}).get('context-1'),
                                'video_1': '',
                                'length': '',
                                'width': '',
                                'height': '',
                                'dimensions_unit': '',
                                'weight': '',
                                'weight_unit': '',
                                'shipping_profile_id': '199606403439',
                                'processing_min': '',
                                'processing_max': '',
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
                                'type': 'physical',
                                'shop_section_id': category_code,
                                'who_made': 'collective',
                                'is_made_to_order': 'TRUE',
                                'is_vintage': 'FALSE',
                                'when_made': 'made_to_order',
                                'should_auto_renew': 'TRUE',
                                'is_taxable': 'TRUE',
                                'is_supply': 'FALSE',
                                'is_customizable': 'FALSE',
                                'is_personalizable': 'FALSE',
                                'personalization_is_required': 'FALSE',
                                'personalization_instructions': '',
                                'personalization_char_count_max': '',
                                'style_1': '',
                                'style_2': '',
                                'tags': tags,
                                'material_1': '',
                                'material_2': '',
                                'material_3': '',
                                'material_4': '',
                                'material_5': '',
                                'material_6': '',
                                'material_7': '',
                                'material_8': '',
                                'material_9': '',
                                'material_10': '',
                                'material_11': '',
                                'material_12': '',
                                'material_13': '',
                                'production_partner_1': '2958232',
                                'production_partner_2': '',
                                'production_partner_3': '',
                                'production_partner_4': '',
                                'production_partner_5': '',
                                'action': 'update',
                                'state': 'draft',
                                'overwrite_images': 'TRUE',
                            })

                            # Split the 'Tags' column into separate columns based on a comma delimiter
                            tags_split = new_data['tags'].str.split(',', expand=True)

                            # Ensure there are 13 columns even if there are no tags
                            for i in range(13):
                                if i not in tags_split.columns:
                                    tags_split[i] = ""

                            # Rename the columns to include the tag name
                            tags_split.columns = [f'tag_{i+1}' for i in range(13)]

                            # Add the new columns to the DataFrame
                            new_data = pd.concat([new_data, tags_split], axis=1)

                            # Drop the original 'Tags' column
                            new_data = new_data.drop('tags', axis=1)

                            # Append the new data to the existing DataFrame
                            products_df = pd.concat([products_df, new_data], ignore_index=True, sort=False)
                            pbar.update(1)


                        else:
                            print(f"Product {product_id} has no enabled variants.")
                    else:
                        print(f"Product {product_id} has no variants.")

                else:
                    print(f"Error retrieving product information for product {product_id}")
                    print(response.status_code)
                    print(response.json())

            else:
                print(f"Error creating product {product_title}")
                print(response.status_code)
        pbar.set_description(f'')
        print("\nProduct creation complete.")
        return products_df