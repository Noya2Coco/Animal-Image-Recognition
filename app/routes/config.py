from flask import Blueprint, render_template, request, redirect, url_for

from config.config import config


config_bp = Blueprint('config', __name__, url_prefix='/config')


@config_bp.route('/')
def home():
    return render_template('config/index.html')


@config_bp.route('/constants', methods=['GET', 'POST'])
def constants():
    if request.method == 'POST':
        config['DEBUG'] = request.form.get('DEBUG') == 'true'
        config['IMAGES_PATH'] = request.form.get('IMAGES_PATH')
        config['MODEL_VERSIONS_PATH'] = request.form.get('MODEL_VERSIONS_PATH')
        config['MODEL_LAST_VERSION'] = request.form.get('MODEL_LAST_VERSION')
        config['ENTITIES_NAMES_PATH'] = request.form.get('ENTITIES_NAMES_PATH')
        config['ENTITIES_DB_PATH'] = request.form.get('ENTITIES_DB_PATH')
        config['ENTITIES_DB_VERSION'] = request.form.get('ENTITIES_DB_VERSION')
        config['TRAIN_IMAGES_PATH'] = request.form.get('TRAIN_IMAGES_PATH')
        config['VALIDATION_IMAGES_PATH'] = request.form.get('VALIDATION_IMAGES_PATH')
        config['EVALUATION_IMAGES_PATH'] = request.form.get('EVALUATION_IMAGES_PATH')
        config['BATCH_SIZE'] = int(request.form.get('BATCH_SIZE'))
        config['NUM_ENTITIES'] = int(request.form.get('NUM_ENTITIES'))
        config['TRAIN_IMAGES_PER_ENTITIES'] = int(request.form.get('TRAIN_IMAGES_PER_ENTITIES'))
        config['VALIDATION_IMAGES_PER_ENTITIES'] = int(request.form.get('VALIDATION_IMAGES_PER_ENTITIES'))
        config['MIN_IMAGE_SIZE_THRESHOLD'] = int(request.form.get('MIN_IMAGE_SIZE_THRESHOLD'))
        # NEED TO ADD NEW CONSTANTS
        
        message = "Constants have been modified"
        
        return redirect(url_for('main.infos', message=message))

    return render_template('config/constants.html', config=config.__dict__)
    