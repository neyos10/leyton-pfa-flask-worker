from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.config import Config


db = SQLAlchemy()


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)

    from app.models.task import Task

    with app.app_context():
        Task.__table__.create(db.engine, checkfirst=True)

    from app.api.routes import api_bp

    app.register_blueprint(api_bp)

    return app
