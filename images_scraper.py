import glob
import hashlib
import json
import os
import re
import requests
import time
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import config
from file_utils import read_animal_list, get_folder_quota_remaining


def hash_url(url):
    """
    Generate an MD5 hash for a given URL.

    Args:
        url (str): The URL to be hashed.

    Returns:
        str: The MD5 hash of the URL.
    """
    return hashlib.md5(url.encode()).hexdigest()


def load_url_filename_mapping(file_path, entity_name=None):
    """
    Load URL-Filename mapping from a JSON file, optionally for a specific entity.

    Args:
        file_path (str): Path to the JSON file.
        entity_name (str, optional): Name of the entity. Defaults to None.

    Returns:
        dict: URL-Filename mapping loaded from the file, or for the specified entity if provided.
    """
    # Check if the file exists and if entity_name is provided
    if os.path.exists(file_path) and entity_name:
        # Load JSON data from the file
        with open(file_path, 'r') as file:
            loaded_data = json.load(file)
            return loaded_data.get(entity_name, {})
    
    # If the file does not exist or entity_name is not provided, return an empty dictionary
    return {}


def save_url_filename_mapping(file_path, entity_name, mapping):
    """
    Save URL-Filename mapping for an entity to a JSON file.

    Args:
        file_path (str): Path to the JSON file.
        entity_name (str): Name of the entity.
        mapping (dict): URL-Filename mapping to be saved.
    """
    existing_mapping = load_url_filename_mapping(file_path)
    existing_mapping[entity_name] = mapping
    
    with open(file_path, 'w') as file:
        json.dump(existing_mapping, file, indent=4)


def save_base64_image(base64_data, filename):
    """
    Save a base64 encoded image data to a file.

    Args:
        base64_data (str): Base64 encoded image data.
        filename (str): Name of the file to save the image.
    """
    # Decode base64 data
    img_data = base64.b64decode(base64_data)
    
    # Write the decoded data to a file
    with open(filename, 'wb') as img_file:
        img_file.write(img_data)


def is_valid_image(url):
    """
    Check if a URL points to a valid image.

    Args:
        url (str): URL of the image.

    Returns:
        bool: True if the image is valid, False otherwise.
    """
    # Check if the URL contains certain keywords indicating non-image files
    if 'logo' in url or 'icon' in url or 'sprite' in url:
        return False
    
    # Check if the URL returns a valid image
    try:
        response = requests.head(url)
        content_type = response.headers['content-type']
        if 'image' in content_type:
            return True
        else:
            return False
    except:
        # If an error occurs (e.g., URL is not reachable), consider it as an invalid image
        return False
            

def get_next_filename(base_dir, query, ext):
    """
    Generate the next filename based on existing files in the directory.

    Args:
        base_dir (str): Base directory path.
        query (str): Query string.
        ext (str): File extension.

    Returns:
        str: The next filename.
    """
    # Get list of existing files in the directory
    existing_files = os.listdir(base_dir)
    
    # Define regex pattern to match filenames
    pattern = re.compile(rf"{query}_(\d+)\.{ext}")
    
    # Extract numbers from existing filenames and sort them in descending order
    existing_numbers = sorted([int(pattern.match(f).group(1)) for f in existing_files if pattern.match(f)], reverse=True)
    
    # Determine the next number in the sequence
    next_number = 0 if not existing_numbers else existing_numbers[0] + 1
    
    # Construct and return the next filename
    return f"{base_dir}/{query}_{next_number}.{ext}"


def adjust_max_images(query_dir, max_images):
    """
    Adjust the maximum number of images based on remaining quota in the directory.

    Args:
        query_dir (str): Directory path for the query.
        max_images (int): Maximum number of images.

    Returns:
        int: Adjusted maximum number of images.
    """
    # Get the remaining quota in the directory
    remaining_quota = get_folder_quota_remaining(query_dir, max_images)
    
    # If remaining quota is less than the maximum number of images,
    # reduce max_images by the amount over the quota
    if remaining_quota < max_images:
        max_images = remaining_quota
        
    return max_images


def delete_last_files(directory, query, max_files, url_filename_mapping_file):
    """
    Delete the last files in a directory and update the URL-Filename mapping file.

    Args:
        directory (str): Path to the directory containing the files.
        query (str): Query string.
        max_files (int): Maximum number of files to delete.
        url_filename_mapping_file (str): Path to the URL-Filename mapping file.
    """
    # List all files in the directory
    files = glob.glob(os.path.join(directory, '*'))
    
    # Sort files by modification date (oldest to newest)
    files.sort(key=os.path.getmtime)
    
    # Ensure max_files is not greater than the number of available files
    num_files_to_delete = min(abs(max_files), len(files))
    
    # Delete the last num_files_to_delete files
    files_to_delete = files[-num_files_to_delete:]
    for file in files_to_delete:
        os.remove(file)
        
        # Remove the reference in the JSON file
        filename = os.path.basename(file)
        url_filename_mapping = load_url_filename_mapping(url_filename_mapping_file, query)
        for key, value in url_filename_mapping.items():
            if value == filename:
                del url_filename_mapping[key]
                break  # Exit the loop once the reference is removed
        
        # Update the JSON file
        save_url_filename_mapping(url_filename_mapping_file, query, url_filename_mapping)
        print(f"Deleted: {file}")
        

def scrape_images(query, max_images, save_dir):
    query_dir = os.path.join(save_dir, query)
    os.makedirs(query_dir, exist_ok=True)
    url_filename_mapping_file = os.path.join(save_dir, 'url_filename_mapping.json')

    # Charge le mapping URL - Nom de fichier pour l'animal spécifié
    url_filename_mapping = load_url_filename_mapping(url_filename_mapping_file, query)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--incognito")

    url = f"https://www.google.com/search?q={query} animal&tbm=isch"
    driver = webdriver.Chrome(options=chrome_options)

    attempts = 0
    max_attempts = 5
    
    while attempts < max_attempts:
        driver.get(url)
        
        try:
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, 'L2AGLb'))
            ).click()
            print("Clicked on the accept button")
            break
        except Exception as e:
            print(f"No accept button found. New try...")
            attempts += 1
            if attempts >= max_attempts:
                print("Max attempts reached, continuing without clicking the accept button")
                break
    
    max_images = adjust_max_images(query_dir, max_images)
    if max_images < 0:
        delete_last_files(query_dir, query, max_images, url_filename_mapping_file)
        return
    
    img_count = 0
    scroll_attempts = 0
    while_index = 1
    last_height = driver.execute_script("return document.body.scrollHeight")

    while img_count < max_images and scroll_attempts < 3:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
        last_height = new_height

        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        images = soup.find_all('img')

        for i, img in enumerate(images):
            if i < 3:
                continue

            img_src = img.get('src') or img.get('data-src')
            
            if img_src and is_valid_image(img_src):
                img_hash = hash_url(img_src)
                if img_hash not in url_filename_mapping:
                    try:
                        if img_src.startswith('data:image'):
                            img_type = img_src.split(';')[0].split('/')[-1]
                            base64_data = img_src.split(',')[1]
                            img_data = base64.b64decode(base64_data)
                            if len(img_data) >= config.MIN_IMAGE_SIZE_THRESHOLD:
                                filename = get_next_filename(query_dir, query, img_type)
                                with open(filename, 'wb') as img_file:
                                    img_file.write(img_data)
                                img_count += 1
                                url_filename_mapping[img_hash] = os.path.basename(filename)
                                print(f"Téléchargée - Hash: {img_hash}, Filename : {filename}")
                                if img_count >= max_images:
                                    break
                        else:
                            if img_src.startswith('/'):
                                img_src = urljoin('https://www.google.com', img_src)
                            response = requests.get(img_src, stream=True)
                            if response.status_code == 200:
                                img_data = response.content
                                if len(img_data) >= config.MIN_IMAGE_SIZE_THRESHOLD:
                                    filename = get_next_filename(query_dir, query, 'jpeg')
                                    with open(filename, 'wb') as img_file:
                                        img_file.write(img_data)
                                    img_count += 1
                                    url_filename_mapping[img_hash] = os.path.basename(filename)
                                    print(f"Téléchargée - Hash: {img_hash}, Filename : {filename} (image sw:/)")
                                    if img_count >= max_images:
                                        break
                    except Exception as e:
                        print(f"Failed to download image {img_src}: {e}")
                else:
                    print(f"Déjà téléchargée - Hash: {img_hash}")

        save_url_filename_mapping(url_filename_mapping_file, query, url_filename_mapping)
        print(f"[Round {while_index}] Total images downloaded: {img_count}")
        while_index += 1
        
    driver.quit()


def scrape_images_for_all_animals(max_images, save_dir):
    animals = read_animal_list()

    for i, animal in enumerate(animals, start=1):
        print(f"\n==========================\n\nScraping images for {animal}... ({i}/{config.NUM_ANIMALS})")
        scrape_images(animal, max_images, save_dir)
        print(f"Finished scraping images for {animal}")


scrape_images_for_all_animals(3, 'tests')
