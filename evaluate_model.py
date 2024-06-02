import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image # type: ignore

import config
from utils.file_utils import get_entity_list


def get_entity_score_and_ranking(prediction, chosen_entity):
    """
    Get the score and ranking of a chosen entity from the prediction.

    Args:
        prediction (list): List of tuples with class names and scores.
        chosen_entity (str): The entity to find in the prediction list.

    Returns:
        tuple: Score and ranking of the chosen entity, or (None, None) if not found.
    """
    for ranking, (entity, score) in enumerate(prediction, start=1):
        if entity == chosen_entity:
            return float(score), ranking
    return None, None


def calculate_statistics(scores, ranks, differences):
    """
    Calculate statistics from prediction scores, rankings, and differences.

    Args:
        scores (list): List of scores.
        ranks (list): List of rankings.
        differences (list): List of score differences.

    Returns:
        dict: Dictionary containing calculated statistics.
    """
    if scores:
        avg_score = f"{round(sum(scores) / len(scores), 2)}%"
        best_score = f"{min(scores)}%"
        worst_score = f"{max(scores)}%"
    else:
        avg_score = best_score = worst_score = None

    if ranks:
        avg_rank = f"{round(sum(ranks) / len(ranks), 2)}/{config.NUM_ANIMALS}"
        best_rank = f"{min(ranks)}/{config.NUM_ANIMALS}"
        worst_rank = f"{max(ranks)}/{config.NUM_ANIMALS}"
    else:
        avg_rank = best_rank = worst_rank = f"0/{config.NUM_ANIMALS}"

    if differences:
        avg_difference = f"+{round(sum(differences) / len(differences), 2)}%"
        min_difference = f"+{min(differences)}%"
        max_difference = f"+{max(differences)}%"
    else:
        avg_difference = min_difference = max_difference = "+0%"

    return {
        "average_scores_percentage": avg_score,
        "best_score_percentage": best_score,
        "worst_score_percentage": worst_score,
        "average_rankings": avg_rank,
        "best_ranking": best_rank,
        "worst_ranking": worst_rank,
        "average_difference_with_best_scores": avg_difference,
        "min_difference_with_best_scores": min_difference,
        "max_difference_with_best_scores": max_difference,
    }


def prediction_image(img_path, model, classes, top_k=10):
    """
    Predict the top classes for an image using a trained model.

    Args:
        img_path (str): Path to the image file.
        model (tf.keras.Model): Trained model for prediction.
        classes (list): List of class names. 
        top_k (int, optional): Number of top predictions to return. Defaults to 5.

    Returns:
        list: List of tuples containing class names and their respective prediction scores.
    """
    # Load and preprocess the image
    img = image.load_img(img_path, target_size=(150, 150))
    img_tensor = image.img_to_array(img)
    img_tensor = np.expand_dims(img_tensor, axis=0)
    img_tensor /= 255.0

    # Predict and get the top k predictions
    predictions = model.predict(img_tensor)[0]
    top_indices = np.argsort(predictions)[::-1][:top_k]

    # Create a list of top k class predictions with scores
    ranked_classes = [(classes[i], predictions[i]) for i in top_indices]

    return ranked_classes


def predictions_all_entities(model):
    """
    Predict classes for all images in the specified directory and calculate statistics.

    Args:
        model (tf.keras.Model): Trained model for prediction.

    Returns:
        dict: Dictionary containing predictions and statistics for each entity.
    """
    # Dictionary to store predictions and statistics for each entity
    predictions = {}
    
    root_path = config.PREDICTION_IMAGES_PATH

    for root_folder, _, files in os.walk(root_path):
        # Skip the parent folder itself
        if root_folder == root_path:
            continue
        
        entity_name = os.path.basename(root_folder)
        
        # Dictionary to store predictions for the current entity
        entity_predictions = {}
        
        # Lists to store scores, rankings, and score differences
        scores = []
        ranks = []
        score_diffs = []

        print(f"\n--- Start prediction for: {entity_name} ---")

        for file in files:
            img_path = os.path.join(root_folder, file)
            
            # Predict the image and get the top predictions
            prediction = prediction_image(img_path, model, get_entity_list(), top_k=config.NUM_ANIMALS)
            
            # Get the score and ranking of the current entity in the predictions
            score, rank = get_entity_score_and_ranking(prediction, entity_name)
            
            # Dictionary to store prediction information for the current image
            prediction_info = {}

            # Handle score and ranking information
            if score:
                score_pct = round(score * 100, 2)
                prediction_info["score_percentage"] = f"{score_pct}%"
                scores.append(score_pct)
            else:
                prediction_info["score_percentage"] = None
                scores.append(0)

            if rank:
                prediction_info["ranking"] = f"{rank}/{config.NUM_ANIMALS}"
                ranks.append(rank)
            else:
                prediction_info["ranking"] = None
                ranks.append(config.NUM_ANIMALS)

            # Handle best entity and score difference information
            if rank and rank > 1:
                best_entity, best_score = prediction[0]
                diff_best_score_pct = round((best_score - score) * 100, 2)
                prediction_info["best_entity"] = best_entity
                prediction_info["best_score_percentage"] = f"{round(best_score * 100, 2)}% (+{diff_best_score_pct}%)"
                score_diffs.append(diff_best_score_pct)
            else:
                prediction_info["best_entity"] = None
                prediction_info["best_score_percentage"] = None
                score_diffs.append(0)

            # Add the prediction information to the entity predictions dictionary
            entity_predictions[file] = prediction_info

        # Calculate and add statistics for the current entity
        stats = calculate_statistics(scores, ranks, score_diffs)
        stats.update(entity_predictions)
        predictions[entity_name] = stats

    return predictions

        



