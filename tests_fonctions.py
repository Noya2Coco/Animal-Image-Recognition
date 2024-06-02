import json
import tensorflow as tf
from file_utils import get_entity_list
from image_scraper import scrape_images

import config
from prediction import predict_all_images


def _scrape_images_for_all_animals(max_images, save_dir):
    animals = get_entity_list()

    for i, animal in enumerate(animals, start=1):
        print(f"\n==========================\n\nScraping images for {animal}... ({i}/{config.NUM_ANIMALS})")
        scrape_images(animal, max_images, save_dir)
        print(f"Finished scraping images for {animal}")


def _prediction_for_all_folders():
    # Load the saved model
    model = tf.keras.models.load_model(f"./models/{config.VERSION}.keras")
    # model = tf.keras.models.load_model('animal_classifier_models/v0.3.h5')
    # model = tf.keras.models.load_model('animal_classifier_models/v0.1.h5')

    predictions = predict_all_images(model)
    print(json.dumps(predictions, indent=4))

if __name__ == "__main__":
    # _scrape_images_for_all_animals(3, 'tests')
    # _prediction_for_all_folders()
    pass