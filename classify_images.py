import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
import numpy as np
import os
import shutil

# Charger le modèle ResNet50 pré-entraîné
model = ResNet50(weights='imagenet')

def classify_and_move_images(image_dir, output_dir):
    for img_name in os.listdir(image_dir):
        img_path = os.path.join(image_dir, img_name)
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        preds = model.predict(x)
        label = decode_predictions(preds, top=1)[0][0][1]

        # Créer un dossier pour chaque label s'il n'existe pas
        label_dir = os.path.join(output_dir, label)
        if not os.path.exists(label_dir):
            os.makedirs(label_dir)

        # Déplacer l'image vers le dossier correspondant
        shutil.move(img_path, os.path.join(label_dir, img_name))

# Exemple d'utilisation
image_dir = 'new_animals'
output_dir = 'new_sorted_images'
classify_and_move_images(image_dir, output_dir)
