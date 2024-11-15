# app/__init__.py
import os
from flask import Flask
from .config import DevelopmentConfig, ProductionConfig
from .main_bp import main_bp

def create_app():
    app = Flask(__name__)
    
    # 根据 FLASK_ENV 环境变量选择配置
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    app.register_blueprint(main_bp)
    
    return app
