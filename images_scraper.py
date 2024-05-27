import time
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import requests
from urllib.parse import urljoin
import config
from file_utils import read_animal_list


def save_base64_image(base64_data, filename):
    img_data = base64.b64decode(base64_data)
    with open(filename, 'wb') as img_file:
        img_file.write(img_data)


def scrape_images(query, max_images, save_dir):
    os.makedirs(save_dir, exist_ok=True)

    # Configure les options du navigateur pour le mode headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--incognito")

    url = f"https://www.google.com/search?q={query} animal&tbm=isch"
    # test with 'photography', 'photo'
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        # Attendre que le bouton soit présent et cliquable, puis cliquer dessus
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'L2AGLb'))
        ).click()
        print("Clicked on the accept button")
    except Exception as e:
        #print(f"No accept button found or error: {e}")
        pass

    time.sleep(2)  # Attendre un peu que la page se charge après avoir accepté

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Faites défiler la page pour charger davantage d'images
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Attendez un moment pour que les images se chargent

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Attendre un peu plus longtemps pour s'assurer que toutes les images sont chargées
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    images = soup.find_all('img')

    print(f"Nombre total d'images trouvées : {len(images)}")

    img_count = 0
    for i, img in enumerate(images):
        # Sauter la première image qui est souvent le logo de Google
        if i == 0 or i == 1 or i == 2:  # Code à améliorer
            continue

        img_src = img.get('src')
        if not img_src:
            img_src = img.get('data-src')
        if img_src:
            # Vérifier si l'image est encodée en base64
            if img_src.startswith('data:image'):
                # Extraire le type de l'image (jpeg, png, etc.) à partir du préfixe data URI
                img_type = img_src.split(';')[0].split('/')[-1]
                # Extraire les données base64 de l'URL
                base64_data = img_src.split(',')[1]
                # Décoder les données base64
                img_data = base64.b64decode(base64_data)
                # Vérifier la taille de l'image pour exclure les icônes potentielles
                if len(img_data) >= config.MIN_IMAGE_SIZE_THRESHOLD:
                    # Enregistrer l'image
                    filename = os.path.join(save_dir, f"{query}_{img_count}.{img_type}")
                    with open(filename, 'wb') as img_file:
                        img_file.write(img_data)
                    img_count += 1
                    if img_count >= max_images:
                        break
            else:
                # Si ce n'est pas une image encodée en base64, télécharger l'image normalement et vérifier la taille
                if img_src.startswith('/'):
                    img_src = urljoin('https://www.google.com', img_src)
                response = requests.get(img_src, stream=True)
                if response.status_code == 200:
                    img_data = response.content
                    # Vérifier la taille de l'image pour exclure les icônes potentielles
                    if len(img_data) >= config.MIN_IMAGE_SIZE_THRESHOLD:
                        # Enregistrer l'image
                        filename = os.path.join(save_dir,
                                                f"{query}_{img_count}.jpg")  # Vous pouvez toujours définir l'extension de fichier comme jpg
                        with open(filename, 'wb') as img_file:
                            img_file.write(img_data)
                        img_count += 1
                        if img_count >= max_images:
                            break

    driver.quit()


def scrape_images_for_all_animals(max_images, base_save_dir):
    animals = read_animal_list()

    for animal in animals:
        print(f"Scraping images for {animal}...")
        save_dir = os.path.join(base_save_dir, animal)
        scrape_images(animal, max_images, save_dir)
        print(f"Finished scraping images for {animal}")


# Exemple d'utilisation
scrape_images_for_all_animals(1, 'animals_prediction')
