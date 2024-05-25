import os
from pprint import pprint
import json
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np

# Charger le modèle enregistré
model = tf.keras.models.load_model('animal_classifier_models/v01.h5')

def predict_image(img_path, model, classes, top_k=5):
    # Charger l'image
    img = image.load_img(img_path, target_size=(150, 150))
    img_tensor = image.img_to_array(img)
    img_tensor = np.expand_dims(img_tensor, axis=0)
    img_tensor /= 255.

    # Faire la prédiction
    predictions = model.predict(img_tensor)[0]  # Récupérer les prédictions
    top_indices = np.argsort(predictions)[::-1][:top_k]  # Indices des top_k prédictions
    
    # Créer le classement des animaux les plus probables
    ranked_classes = [(classes[i], predictions[i]) for i in top_indices]
    
    return ranked_classes

def read_animal_list(file_path):
    with open(file_path, 'r') as file:
        animals = [line.strip() for line in file.readlines()]
    return animals

def get_animal_score_and_ranking(prediction, chosen_animal):
    for ranking, (animal, score) in enumerate(prediction, start=1):
        if animal == chosen_animal:
            return float(score), ranking
    return None, None
    
# Lire la liste des animaux
animals = read_animal_list("animals.txt")

def predict_all_images():
    predictions = {}
    root_path = "animals/predict"
    for dossier_racine, sous_dossiers, fichiers in os.walk(root_path):
        animal = os.path.basename(dossier_racine)
        print(f"\n--- Start the prediction for : {animal} ---")
        for fichier in fichiers:
            image_path = os.path.join(dossier_racine, fichier)
            
            prediction = predict_image(image_path, model, animals, top_k=90)
            print(prediction)
            animal_score, animal_ranking = get_animal_score_and_ranking(prediction, os.path.basename(dossier_racine))
            
            predictions[os.path.basename(dossier_racine)] = {
                "score" : animal_score,
            }
            
            if animal_score is not None:
                predictions[os.path.basename(dossier_racine)]["score_percentage"] = str(round(animal_score*100, 2)) + "%"
            else:
                predictions[os.path.basename(dossier_racine)]["score_percentage"] = "-%"
                
            if animal_ranking is not None:
                predictions[os.path.basename(dossier_racine)]["ranking"] = str(animal_ranking) + "/90"
            else:
                predictions[os.path.basename(dossier_racine)]["ranking"] = "-/90"
        
    return predictions

# Exemple d'utilisation
predictions = predict_all_images()
print(json.dumps(predictions, indent=4))
