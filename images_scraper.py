import os
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
from file_utils import read_animal_list, check_folder_image_quota


def is_valid_image(url):
    # Check if the image is not an icon or a very small image
    if 'logo' in url or 'icon' in url or 'sprite' in url:
        return False
    return True


def save_base64_image(base64_data, filename):
    img_data = base64.b64decode(base64_data)
    with open(filename, 'wb') as img_file:
        img_file.write(img_data)


def scrape_images(query, max_images, save_dir):
    os.makedirs(save_dir, exist_ok=True)

    # Configure browser options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--incognito")

    url = f"https://www.google.com/search?q={query} animal&tbm=isch"
    # url = f"https://www.google.com/search?q={query} photo&tbm=isch"
    # url = f"https://www.google.com/search?q={query} photography&tbm=isch"
    driver = webdriver.Chrome(options=chrome_options)

    attempts = 0
    max_attempts = 5
    
    while attempts < max_attempts:
        driver.get(url)
        
        try:
            # Waiting until the button 'Tout accepter' is clickable (cookies)
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

    img_count = 0
    scroll_attempts = 0
    while_index = 1
    last_height = driver.execute_script("return document.body.scrollHeight")
    downloaded_urls = set()  # Keep downloaded image URLs

    while img_count < max_images and scroll_attempts < 3:
        # Page scroll
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for all images to load 

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
        last_height = new_height

        time.sleep(2) # Wait for all images to load 
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        images = soup.find_all('img')

        for i, img in enumerate(images):
            # The first images are often those from Google
            if i < 3:
                continue

            img_src = img.get('src') or img.get('data-src')
            if img_src and is_valid_image(img_src) and img_src not in downloaded_urls:
                try:
                    if img_src.startswith('data:image'):
                        img_type = img_src.split(';')[0].split('/')[-1]
                        base64_data = img_src.split(',')[1]
                        img_data = base64.b64decode(base64_data)
                        if len(img_data) >= config.MIN_IMAGE_SIZE_THRESHOLD:
                            filename = os.path.join(save_dir, f"{query}_{img_count}.{img_type}")
                            with open(filename, 'wb') as img_file:
                                img_file.write(img_data)
                            img_count += 1
                            downloaded_urls.add(img_src)  # Add to set of downloaded URLs
                            if img_count >= max_images:
                                break
                    else:
                        if img_src.startswith('/'):
                            img_src = urljoin('https://www.google.com', img_src)
                        response = requests.get(img_src, stream=True)
                        if response.status_code == 200:
                            img_data = response.content
                            if len(img_data) >= config.MIN_IMAGE_SIZE_THRESHOLD:
                                filename = os.path.join(save_dir, f"{query}_{img_count}.jpg")
                                with open(filename, 'wb') as img_file:
                                    img_file.write(img_data)
                                img_count += 1
                                downloaded_urls.add(img_src)  # Add to set of downloaded URLs
                                if img_count >= max_images:
                                    break
                except Exception as e:
                    print(f"Failed to download image {img_src}: {e}")

        print(f"[Round {while_index}] Total images downloaded: {img_count}")
        while_index += 1
        
    driver.quit()


def scrape_images_for_all_animals(max_images, base_save_dir):
    animals = read_animal_list()

    for i, animal in enumerate(animals, start=1):
        print(f"\n==========================\nScraping images for {animal}... ({i}/{config.NUM_ANIMALS})")
        save_dir = os.path.join(base_save_dir, animal)
        scrape_images(animal, max_images, save_dir)
        print(f"Finished scraping images for {animal}")


scrape_images_for_all_animals(1000, 'test')
