import os
import shutil
import random

def move_files(src_dir, dest_dir, percentage):
    # Créez les répertoires de destination s'ils n'existent pas
    os.makedirs(dest_dir, exist_ok=True)
    
    # Liste des fichiers dans le répertoire source
    files = os.listdir(src_dir)
    
    # Sélectionnez aléatoirement un pourcentage de fichiers
    num_files_to_move = int(len(files) * percentage)
    files_to_move = random.sample(files, num_files_to_move)
    
    # Déplacez les fichiers sélectionnés
    for file in files_to_move:
        shutil.move(os.path.join(src_dir, file), os.path.join(dest_dir, file))

def read_animal_list(file_path):
    with open(file_path, 'r') as file:
        animals = [line.strip() for line in file.readlines()]
    return animals

# Chemins des répertoires
base_dir = 'animals'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')

# Classes d'animaux
animals = read_animal_list("animals.txt")

# Déplacer 20% des images de chaque classe
for animal_class in animals:
    src_dir = os.path.join(train_dir, animal_class)
    dest_dir = os.path.join(validation_dir, animal_class)
    move_files(src_dir, dest_dir, 0.20)
