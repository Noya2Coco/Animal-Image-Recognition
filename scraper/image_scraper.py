import os
import time
import base64
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import config.config as config
from utils.file_utils import adjust_max_files, delete_last_files, get_next_filename
from utils.image_utils import is_valid_image
from utils.url_utils import hash_url, load_url_filename_mapping, save_url_filename_mapping


def setup_chrome_options():
    """
    Setup and return Chrome options for headless browsing.
    
    Returns:
        Options: Configured Chrome options.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--incognito")
    return chrome_options


def handle_accept_button(driver, max_attempts=5):
    """
    Handle the acceptance of cookies or other pop-ups on the webpage.

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        max_attempts (int): Maximum number of attempts to find and click the accept button.
    """
    attempts = 0
    while attempts < max_attempts:
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


def scroll_and_collect_images(driver, max_images):
    """
    Scroll the webpage and collect image elements.

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        max_images (int): Maximum number of images to collect.

    Returns:
        list: Collected image elements.
    """
    img_count = 0
    scroll_attempts = 0
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

        img_count = len(images) - 3  # Skip the first three images
        if img_count >= max_images:
            break

    return images


def process_image(img_src, entity_dir, entity, url_filename_mapping, img_count, max_images):
    """
    Process and save the image from the given source URL.

    Args:
        img_src (str): Image source URL.
        entity_dir (str): Directory to save the image.
        entity (str): Entity string.
        url_filename_mapping (dict): URL to filename mapping.
        url_filename_mapping_file (str): Path to the URL-Filename mapping file.
        img_count (int): Current image count.
        max_images (int): Maximum number of images to save.

    Returns:
        int: Updated image count.
    """
    img_hash = hash_url(img_src)
    if img_hash not in url_filename_mapping.values():
        try:
            if img_src.startswith('data:image'):
                img_type = img_src.split(';')[0].split('/')[-1]
                base64_data = img_src.split(',')[1]
                img_data = base64.b64decode(base64_data)
                if len(img_data) >= config.MIN_IMAGE_SIZE_THRESHOLD:
                    filename = get_next_filename(entity_dir, entity, img_type)
                    with open(filename, 'wb') as img_file:
                        img_file.write(img_data)
                    img_count += 1
                    url_filename_mapping[os.path.basename(filename)] = img_hash
                    print(f"Downloaded - Hash: {img_hash}, Filename: {filename}")
            else:
                if img_src.startswith('/'):
                    img_src = urljoin('https://www.google.com', img_src)
                response = requests.get(img_src, stream=True)
                if response.status_code == 200:
                    img_data = response.content
                    if len(img_data) >= config.MIN_IMAGE_SIZE_THRESHOLD:
                        filename = get_next_filename(entity_dir, entity, 'jpeg')
                        with open(filename, 'wb') as img_file:
                            img_file.write(img_data)
                        img_count += 1
                        url_filename_mapping[os.path.basename(filename)] = img_hash
                        print(f"Downloaded - Hash: {img_hash}, Filename: {filename}")
            if img_count >= max_images:
                return img_count
        except Exception as e:
            print(f"Failed to download image {img_src}: {e}")
    else:
        print(f"Already downloaded - Hash: {img_hash}")
    return img_count


def scrape_images(entity, max_images, save_dir):
    """
    Scrape images from Google Images based on the entity and save them to the specified directory.

    Args:
        entity (str): Entity string to search for images.
        max_images (int): Maximum number of images to download.
        save_dir (str): Directory to save the downloaded images.
    """
    entity_dir = os.path.join(save_dir, entity)
    os.makedirs(entity_dir, exist_ok=True)
    url_filename_mapping_file = os.path.join(save_dir, 'url_filename_mapping.json')

    # Load URL to Filename mapping for the specified entity
    url_filename_mapping = load_url_filename_mapping(url_filename_mapping_file, entity)

    chrome_options = setup_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    url = f"https://www.google.com/search?q={entity} animal&tbm=isch"
    driver.get(url)

    handle_accept_button(driver)

    max_images = adjust_max_files(entity_dir, max_images)
    if max_images <= 0:
        delete_last_files(entity_dir, entity, abs(max_images), url_filename_mapping_file)
        return

    images = scroll_and_collect_images(driver, max_images)

    img_count = 0
    for i, img in enumerate(images):
        if i < 3:
            continue

        img_src = img.get('src') or img.get('data-src')
        if img_src and is_valid_image(img_src):
            img_count = process_image(img_src, entity_dir, entity, url_filename_mapping, img_count, max_images)
            if img_count >= max_images:
                break

    save_url_filename_mapping(url_filename_mapping_file, entity, url_filename_mapping)
    print(f"Total images downloaded: {img_count}")

    driver.quit()
