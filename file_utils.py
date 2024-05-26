import os
import shutil
import random

def read_animal_list(file_path):
    with open(file_path, 'r') as file:
        animals = [line.strip() for line in file.readlines()]
    return animals

def check_image_quota(base_dir, num_files):
    folders_with_less_than_num_images = []
    folders = os.listdir(base_dir)

    for folder in folders:
        folder_path = os.path.join(base_dir, folder)

        if os.path.isdir(folder_path):
            # How many images in the folder
            num_images = len(os.listdir(folder_path))
            if num_images != num_files:
                folders_with_less_than_num_images.append(folder)

    if len(folders_with_less_than_num_images):
        return folders_with_less_than_num_images
    
    return None

def move_files(src_dir, dest_dir, percentage):
    os.makedirs(dest_dir, exist_ok=True)
    files = os.listdir(src_dir)
    
    # Randomly select a percentage of files
    num_files_to_move = int(len(files) * percentage)
    files_to_move = random.sample(files, num_files_to_move)
    
    # Move selected files
    for file in files_to_move:
        shutil.move(os.path.join(src_dir, file), os.path.join(dest_dir, file))


def _move_20percents_files():
    # Chemins des répertoires
    base_dir = 'animals_v02'
    train_dir = os.path.join(base_dir, 'train')
    validation_dir = os.path.join(base_dir, 'validation')

    # Classes d'animaux
    animals = read_animal_list("animals.txt")

    # Déplacer 20% des images de chaque classe
    for animal_class in animals:
        src_dir = os.path.join(train_dir, animal_class)
        dest_dir = os.path.join(validation_dir, animal_class)
        move_files(src_dir, dest_dir, 0.20)
