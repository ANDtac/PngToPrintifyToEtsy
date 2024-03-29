from tqdm import tqdm
import requests
import os
import json

printify_base_url = "https://api.printify.com/v1"
printify_api_key = ''
image_ids = []
def printify_upload(image_urls, image_files):
    print(f'Uploading {len(image_files)} files to Printify')
    # Initialize the progress bar outside of the loop
    with tqdm(total=len(image_files), ncols=70, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}', leave=False) as pbar:
        # Loop through each image file and its corresponding url
        for (image_file_path, _), image_url in zip(image_files, image_urls):
                # Upload the image to Printify and get the image ID
                headers = {
                    "Authorization": f"Bearer {printify_api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Python/3.9 Requests/2.28.2 VisualStudio/17.5.3",
                }
                params = {
                    "file_name": os.path.basename(image_file_path),
                    "url": image_url,
                }
                image_upload_url = printify_base_url + '/uploads/images.json'

                pbar.set_description(f"Uploading {os.path.basename(image_file_path)} to Printify")
               

                response = requests.post(image_upload_url, headers=headers, json=params)                
                if response.status_code == 200:
                    image_id = response.json()['id']
                    image_ids.append(image_id)
                    pbar.update(1)
                else:
                    print(f"Error uploading image {image_url}")
                    print(response.status_code)
                    response_json = response.json()
                    response_json_string = json.dumps(response_json, indent=4)
                    print(response_json_string)
                
        pbar.set_description(f'')
        print("\nUpload to Printify complete.")
        return image_ids
