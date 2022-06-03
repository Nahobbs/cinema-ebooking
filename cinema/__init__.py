import logging

from flask import Flask, url_for, render_template
from werkzeug.utils import redirect

from configuration import config
from . import user, admin, email, booking, checkout
from .user import _encrypt_password


def create_app():
    """Initializes Flask Application"""
    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)
    app.config['MAIL_SERVER'] = config['confirmation_email']['smtp_server']
    app.config['MAIL_USERNAME'] = config['confirmation_email']['sending_email']
    app.config['MAIL_PASSWORD'] = config['confirmation_email']['email_password']
    app.config['MAIL_USE_TLS'] = True
    app.secret_key = config['session']['secret_key']

    blueprints = {user.bp, admin.bp, email.bp, booking.bp, checkout.bp}
    for bp in blueprints:
        app.register_blueprint(bp)
    set_routes(app)
    return app


def set_routes(app):
    @app.route('/')
    def index():
        return redirect(url_for('user.view'))

    return app
