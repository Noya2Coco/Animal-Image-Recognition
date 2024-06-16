from flask import Flask

from config import config

def create_app():
    app = Flask(__name__)
    
    # Update Flask app config with the loaded config
    app.config.update(config.__dict__)
    
    from .app import main
    app.register_blueprint(main)
    
    from .routes.config import config_bp
    app.register_blueprint(config_bp)
    
    from .routes.recognition import recognition_bp
    app.register_blueprint(recognition_bp)
    
    return app
