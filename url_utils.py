import os
import json
import hashlib


def hash_url(url):
    """
    Generate an MD5 hash for a given URL.

    Args:
        url (str): The URL to be hashed.

    Returns:
        str: The MD5 hash of the URL.
    """
    return hashlib.md5(url.encode()).hexdigest()


def load_url_filename_mapping(file_path, entity_name=None):
    """
    Load URL-Filename mapping from a JSON file, optionally for a specific entity.

    Args:
        file_path (str): Path to the JSON file.
        entity_name (str, optional): Name of the entity for which to load the mapping. Defaults to None.

    Returns:
        dict: URL-Filename mapping loaded from the file. If an entity name is provided, returns the mapping for that specific entity, otherwise returns the entire mapping.
    """
    # Check if the file exists
    if os.path.exists(file_path):
        # Load JSON data from the file
        with open(file_path, 'r') as file:
            loaded_data = json.load(file)
            # Check if the entity_name is provided
            if entity_name:
                return loaded_data.get(entity_name, {})
            
            # If entity_name is not provided, return all the entities
            return loaded_data
    
    # If the file does not exist, return an empty dictionary
    return {}


def save_url_filename_mapping(file_path, entity_name, mapping):
    """
    Save URL-Filename mapping for an entity to a JSON file.

    Args:
        file_path (str): Path to the JSON file.
        entity_name (str): Name of the entity.
        mapping (dict): URL-Filename mapping to be saved.
    """
    existing_mapping = load_url_filename_mapping(file_path)
    existing_mapping[entity_name] = mapping
    
    with open(file_path, 'w') as file:
        json.dump(existing_mapping, file, indent=4)