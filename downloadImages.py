import os
import requests
from PIL import Image
from io import BytesIO

# Define the directory for temporary image storage
TEMP_IMAGE_DIR = 'temp_images'

# Ensure the directory exists
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)


def download_images(image_urls):
    """
    Downloads images from given URLs and saves them in a temporary directory.
    Returns a list of paths to the downloaded images.
    """
    # Delete any existing images in the directory
    for filename in os.listdir(TEMP_IMAGE_DIR):
        os.remove(os.path.join(TEMP_IMAGE_DIR, filename))

    # Download and save each image
    image_paths = []
    for url in image_urls:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we got the image data
        image = Image.open(BytesIO(response.content))

        # Save the image
        image_path = os.path.join(TEMP_IMAGE_DIR, f'image{len(image_paths)+1}.jpg')
        image.save(image_path, 'JPEG')
        image_paths.append(image_path)

    return image_paths