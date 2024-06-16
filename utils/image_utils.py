import requests
import base64


def is_valid_image(url):
    """
    Check if a URL points to a valid image.

    Args:
        url (str): URL of the image.

    Returns:
        bool: True if the image is valid, False otherwise.
    """
    # Check if the URL contains certain keywords indicating non-image files
    if 'logo' in url or 'icon' in url or 'sprite' in url:
        return False
    
    # Check if the URL returns a valid image
    try:
        response = requests.head(url)
        content_type = response.headers['content-type']
        if 'image' in content_type:
            return True
        else:
            return False
    except:
        # If an error occurs (e.g., URL is not reachable), consider it as an invalid image
        return False
    

def is_image(filename):
    """
    Check if a filename has an allowed image extension.

    Args:
        filename (str): The filename to check.

    Returns:
        bool: True if the filename has an allowed image extension, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

    
    
def save_base64_image(base64_data, filename):
    """
    Save a base64 encoded image data to a file.

    Args:
        base64_data (str): Base64 encoded image data.
        filename (str): Name of the file to save the image.
    """
    # Decode base64 data
    img_data = base64.b64decode(base64_data)
    
    # Write the decoded data to a file
    with open(filename, 'wb') as img_file:
        img_file.write(img_data)
        
        

