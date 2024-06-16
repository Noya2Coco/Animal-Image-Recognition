import os
import re
import shutil
import random
import glob

from config.config import config
from utils.url_utils import load_url_filename_mapping, save_url_filename_mapping


def get_entity_list(file_path=config["ENTITIES_NAMES_PATH"]):
    """
    Read and return a list of entities from a file.

    Args:
        file_path (str): Path to the file containing the list of entities.

    Returns:
        list: List of entities read from the file.
    """
    with open(file_path, 'r') as file:
        entities = [line.strip() for line in file.readlines()]
    return entities


def count_files_in_directory(directory):
    """
    Count the number of files in a given directory.

    Args:
        directory (str): Path to the directory.

    Returns:
        int: Number of files in the directory.
    """
    if os.path.isdir(directory):
        return len(os.listdir(directory))
    return 0


def check_folders_image_quota(base_dir, num_files):
    """
    Check which folders in the base directory contain less than a specified number of images.

    Args:
        base_dir (str): Base directory containing folders.
        num_files (int): Number of files to check against.

    Returns:
        list: Folders with less than the specified number of images, or None if all folders meet the quota.
    """
    # List to store the names of folders that do not meet the image quota
    folders_with_less_than_num_images = []
    
    folders = os.listdir(base_dir)

    for folder in folders:
        folder_path = os.path.join(base_dir, folder)

        # Check if the current item is a directory
        if os.path.isdir(folder_path):
            num_images = count_files_in_directory(folder_path)
            
            if num_images != num_files:
                folders_with_less_than_num_images.append(folder)

    # Return the list of folders if any do not meet the quota, otherwise return None
    return folders_with_less_than_num_images if folders_with_less_than_num_images else None


def get_folder_quota_remaining(base_dir, max_nb_files):
    """
    Calculate the remaining quota of files for a given directory.

    Args:
        base_dir (str): Base directory path.
        max_nb_files (int): Maximum number of files allowed in the directory.

    Returns:
        int: Remaining number of files that can be added to the directory.
    """
    num_files = count_files_in_directory(base_dir)
    return max_nb_files - num_files


def adjust_max_files(entity_dir, max_images):
    """
    Adjust the maximum number of images based on remaining quota in the directory.

    Args:
        entity_dir (str): Directory path for the entity.
        max_images (int): Maximum number of images.

    Returns:
        int: Adjusted maximum number of images.
    """
    remaining_quota = get_folder_quota_remaining(entity_dir, max_images)
    return min(max_images, remaining_quota)


def get_next_filename(base_dir, entity, ext):
    """
    Generate the next filename based on existing files in the directory.

    Args:
        base_dir (str): Base directory path.
        entity (str): Entity string.
        ext (str): File extension.

    Returns:
        str: The next filename.
    """
    existing_files = os.listdir(base_dir)
    
    # Define regex pattern to match filenames
    pattern = re.compile(rf"{entity}_(\d+)\.{ext}")
    
    # Extract numbers from existing filenames and sort them in descending order
    existing_numbers = sorted([int(pattern.match(f).group(1)) for f in existing_files if pattern.match(f)], reverse=True)
    
    # Determine the next number in the sequence
    next_number = 0 if not existing_numbers else existing_numbers[0] + 1
    
    return f"{base_dir}/{entity}_{next_number}.{ext}"


def delete_last_files(directory, entity, max_files, url_filename_mapping_file):
    """
    Delete the last files in a directory and update the URL-Filename mapping file.

    Args:
        directory (str): Path to the directory containing the files.
        entity (str): Entity string.
        max_files (int): Maximum number of files to delete.
        url_filename_mapping_file (str): Path to the URL-Filename mapping file.
    """
    if max_files <= 0:
        return
    
    files = glob.glob(os.path.join(directory, '*'))
    
    # Sort files by modification date (oldest to newest)
    files.sort(key=os.path.getmtime)
    
    # Ensure max_files is not greater than the number of available files
    num_files_to_delete = min(max_files, len(files))
    
    # Delete the last num_files_to_delete files
    files_to_delete = files[-num_files_to_delete:]
    for file in files_to_delete:
        os.remove(file)
        
        # Remove the reference in the JSON file
        filename = os.path.basename(file)
        url_filename_mapping = load_url_filename_mapping(url_filename_mapping_file, entity)
        for key, value in url_filename_mapping.items():
            if key == filename:
                del url_filename_mapping[key]
                break  # Exit the loop once the reference is removed
        
        # Update the JSON file
        save_url_filename_mapping(url_filename_mapping_file, entity, url_filename_mapping)
        print(f"Deleted: {file}")
        

def move_files(src_dir, dest_dir, percentage):
    """
    Move a percentage of files from the source directory to the destination directory.

    Args:
        src_dir (str): Source directory path.
        dest_dir (str): Destination directory path.
        percentage (float): Percentage of files to move.
    """
    os.makedirs(dest_dir, exist_ok=True)
    files = os.listdir(src_dir)

    # Randomly select a percentage of files to move
    num_files_to_move = int(len(files) * percentage)
    files_to_move = random.sample(files, num_files_to_move)

    # Move the selected files
    for file in files_to_move:
        shutil.move(os.path.join(src_dir, file), os.path.join(dest_dir, file))
        
        
def get_files_ext(dir, ext):
    """
    Get a list of files with a specific extension in a given directory.

    Args:
        dir (str): The directory path to search in.
        ext (str): The file extension to search for (e.g., '.txt').

    Returns:
        list: A list of filenames (with the specified extension) found in the directory.
    """
    # Create a search pattern for files with the specified extension in the given directory.
    pattern = os.path.join(dir, f'*{ext}')
    
    # Use glob to find all files matching the pattern and return their base names.
    return [os.path.basename(file) for file in glob.glob(pattern)]

