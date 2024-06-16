import os
import json
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

from config.config import config
from utils.file_utils import get_files_ext
from utils.image_utils import is_image
from utils.model_utils import load_model
from evaluate.evaluate_model import prediction_image


recognition_bp = Blueprint('recognition', __name__, url_prefix='/recognition')


@recognition_bp.route('/')
def home():
    models = get_files_ext(config["MODEL_VERSIONS_PATH"], "h5")
    models += get_files_ext(config["MODEL_VERSIONS_PATH"], "keras")
    
    return render_template('recognition/index.html', models=models)


@recognition_bp.route('/result', methods=['GET', 'POST'])
def result():
    model = request.form.get('model')
    
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'No file part'
        
        file = request.files['image']
        
        if file.filename == '':
            return 'No selected file'
        
        if file and is_image(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(config['UPLOADS_PATH'], filename)
            file.save(file_path)
            
            #result = process_image_with_model(file_path, model)
            prediction = prediction_image(file_path, load_model(model))
            
            file_obj = Path(file_path)
            if file_obj.exists():
                file_obj.unlink()
                
            return render_template('recognition/result.html', model=model, prediction=prediction, filename=filename)
        else:
            return 'File type not allowed'
            
    return redirect(url_for('recognition.home'))
    
