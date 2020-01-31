import os

import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from shadow.blueprints.auth import auth_bp
from shadow.blueprints.agent import agent_bp
from shadow.blueprints.api import api
from shadow.blueprints.socketio import socketio_bp
# from shadow.blueprints.oauth import oauth_bp
from shadow.extensions import db, login_manager, csrf, socketio
from shadow.models import User
from shadow.config import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('shadow')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_errors(app)
    register_commands(app)

    return app


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(api)
    app.register_blueprint(socketio_bp)
    # app.register_blueprint(oauth_bp)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error.html', description=e.description, code=e.code), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', description=e.description, code=e.code), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', description='Internal Server Error', code='500'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('error.html', description=e.description, code=e.code), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--message', default=300, help='Quantity of messages, default is 300.')
    def forge():

        click.echo('Initializing the database...')
        db.drop_all()
        db.create_all()

        click.echo('Forging the data...')
        admin = User(nickname='Sun', email='ideasource@foxmail.com')
        admin.set_password('sunyue2332030')
        db.session.add(admin)
        db.session.commit()
        click.echo('Done.')