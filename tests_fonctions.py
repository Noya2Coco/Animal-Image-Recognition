import json
import os
import pandas as pd
import tensorflow as tf
from graphics import make_bar_plot_avg_difference_best_scores, make_bar_plot_avg_scores, make_box_plot_avg_rankings, make_box_plot_avg_score_percentage, transform_format_data
from utils.file_utils import get_entity_list, move_files
from image_scraper import scrape_images

import config
from evaluate_model import predictions_all_entities


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

    predictions = predictions_all_entities(model)
    print(json.dumps(predictions, indent=4))
    
    
def _move_20percents_files():
    # Chemins des répertoires
    base_dir = 'animals_v02'
    train_dir = os.path.join(base_dir, 'train')
    validation_dir = os.path.join(base_dir, 'validation')

    animals = get_entity_list()

    # Déplacer 20% des images de chaque classe
    for animal_class in animals:
        src_dir = os.path.join(train_dir, animal_class)
        dest_dir = os.path.join(validation_dir, animal_class)
        move_files(src_dir, dest_dir, 0.20)


def _make_evaluation_graphics():
    model = tf.keras.models.load_model(f"./models/{config.VERSION}.keras")
    predictions = predictions_all_entities(model)
    print(predictions)
    global_data, individual_data = transform_format_data(predictions)
    global_df = pd.DataFrame(global_data)
    individual_df = pd.DataFrame(individual_data)
    
    make_bar_plot_avg_scores(global_df)
    make_bar_plot_avg_difference_best_scores(global_df)
    make_box_plot_avg_score_percentage(individual_df)
    make_box_plot_avg_rankings(individual_df)


if __name__ == "__main__":
    # _scrape_images_for_all_animals(3, 'tests')
    # _prediction_for_all_folders()
    # _move_20percents_files()
    _make_evaluation_graphics()
    pass