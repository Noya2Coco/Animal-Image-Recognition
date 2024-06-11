import os
from flask import Blueprint, Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

from config.config import config
from utils.file_utils import check_folders_image_quota, get_entity_list


main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')


@main.route('/infos')
def infos():
    paths = {}
    paths["entities_dataset"] = config["ENTITIES_DB_PATH"]
    paths["train_imgs"] = config["TRAIN_IMAGES_PATH"]
    paths["validation_imgs"] = config["VALIDATION_IMAGES_PATH"]
    paths["evaluation_imgs"] = config["EVALUATION_IMAGES_PATH"]
    
    infos = {}
    infos["entities_list"] = get_entity_list()        
    infos["entities_train_not_quota"] = check_folders_image_quota(config["TRAIN_IMAGES_PATH"], config["TRAIN_IMAGES_PER_ENTITIES"])
    infos["entities_validation_not_quota"] = check_folders_image_quota(config["VALIDATION_IMAGES_PATH"], config["VALIDATION_IMAGES_PER_ENTITIES"])
    
    message = request.args.get('message')
     
    return render_template('infos.html', paths=paths, infos=infos, message=message)
    

@main.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return 'No image uploaded', 400
    file = request.files['image']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        result = 0
        # result = predict_animal(file_path)
        os.remove(file_path)
        return render_template('result.html', result=result)
