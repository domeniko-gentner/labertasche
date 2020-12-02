#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
import logging
from flask import Flask, redirect, url_for
from flask_cors import CORS
from sqlalchemy import event
# noinspection PyProtectedMember
from sqlalchemy.engine import Engine
from labertasche.settings import Settings
from labertasche.database import labertasche_db
from labertasche.blueprints import bp_comments, bp_login, bp_dashboard
from labertasche.helper import User
from flask_login import LoginManager
from flask_migrate import Migrate


# Load settings
settings = Settings()

# Flask App
laberflask = Flask(__name__)
laberflask.config.update(dict(
    SESSION_COOKIE_DOMAIN=settings.system['cookie-domain'],
    DEBUG=settings.system['debug'],
    SECRET_KEY=settings.system['secret'],
    TEMPLATES_AUTO_RELOAD=True,
    SQLALCHEMY_DATABASE_URI=settings.system['database_uri'],
    SQLALCHEMY_TRACK_MODIFICATIONS=False
))

# flask migrate
migrate = Migrate(laberflask, labertasche_db, render_as_batch=True)

# CORS
CORS(laberflask, resources={r"/comments": {"origins": settings.system['blog_url']}})

# Import blueprints
laberflask.register_blueprint(bp_comments)
laberflask.register_blueprint(bp_dashboard)
laberflask.register_blueprint(bp_login)

# Disable Werkzeug's verbosity during development
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Initialize ORM
labertasche_db.init_app(laberflask)
with laberflask.app_context():
    labertasche_db.create_all()

# Set up login manager
loginmgr = LoginManager(laberflask)
loginmgr.login_view = 'bp_admin_login.login'


@loginmgr.user_loader
def user_loader(user_id):
    if user_id != "0":
        return None
    return User(user_id)


@loginmgr.unauthorized_handler
def login_invalid():
    return redirect(url_for('bp_login.show_login'))


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if settings.system["database_uri"][0:6] == 'sqlite':
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()
