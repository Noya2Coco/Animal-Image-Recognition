import os

# Chemin vers le répertoire contenant les dossiers d'images
base_dir = 'animals/train'
num_files = 48
# num_files = 48

# Liste pour stocker les noms des dossiers avec moins de 48 images
folders_with_less_than_num_images = []
number_of_folder = 0
# Parcourir tous les dossiers dans le répertoire
for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    # Vérifier si le chemin est un répertoire
    if os.path.isdir(folder_path):
        # Compter le nombre d'images dans le dossier
        num_images = len(os.listdir(folder_path))
        if num_images != num_files:
            folders_with_less_than_num_images.append(folder)
            
    number_of_folder +=1


# Vérifier s'il y a des dossiers avec moins de 48 images
if len(folders_with_less_than_num_images) == 0:
    print(f"Les {number_of_folder} dossiers ont {num_files} images.")
else:
    print(f"Les dossiers suivants n'ont pas {num_files} images :")
    for folder in folders_with_less_than_num_images:
        print(folder)
