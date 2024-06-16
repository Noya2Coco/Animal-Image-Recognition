import tensorflow as tf

from config.config import config


def load_model(model_file):
    """
    Load a Keras model from the specified model file.

    Args:
        model_file (str): Name of the model file to load.

    Returns:
        tf.keras.Model: Loaded Keras model object.
    """
    model_path = f"{config['MODEL_VERSIONS_PATH']}{model_file}"
    return tf.keras.models.load_model(model_path)