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
from sqlalchemy import event, inspect
# noinspection PyProtectedMember
from sqlalchemy.engine import Engine
from labertasche.settings import Settings
from labertasche.database import labertasche_db
from labertasche.blueprints import bp_comments, bp_login, bp_dashboard, bp_jsconnector, bp_dbupgrades
from labertasche.helper import User
from flask_login import LoginManager
from datetime import timedelta

# Load settings
settings = Settings()

# Flask App
laberflask = Flask(__name__)
laberflask.config.update(dict(
    SESSION_COOKIE_DOMAIN=settings.system['cookie_domain'],
    SESSION_COOKIE_SECURE=settings.system['cookie_secure'],
    REMEMBER_COOKIE_SECURE=settings.system['cookie_secure'],
    REMEMBER_COOKIE_DURATION=timedelta(days=7),
    REMEMBER_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST=True,
    DEBUG=settings.system['debug'],
    SECRET_KEY=settings.system['secret'],
    TEMPLATES_AUTO_RELOAD=settings.system['debug'],
    SQLALCHEMY_DATABASE_URI=settings.system['database_uri'],
    SQLALCHEMY_TRACK_MODIFICATIONS=False
))

# CORS
CORS(laberflask, resources={r"/comments": {"origins": settings.system['blog_url']},
                            r"/api": {"origins": settings.system['web_url']},
                            r"/dashboard": {"origins": settings.system['web_url']},
                            })

# Import blueprints
laberflask.register_blueprint(bp_comments)
laberflask.register_blueprint(bp_dashboard)
laberflask.register_blueprint(bp_login)
laberflask.register_blueprint(bp_jsconnector)
laberflask.register_blueprint(bp_dbupgrades)

# Disable Werkzeug's verbosity during development
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Set up login manager
loginmgr = LoginManager(laberflask)
loginmgr.login_view = 'bp_admin_login.login'

# Initialize ORM
labertasche_db.init_app(laberflask)
with laberflask.app_context():
    table_names = inspect(labertasche_db.get_engine()).get_table_names()
    is_empty = table_names == []
    # Only create tables if the db is empty, so we can do a controlled upgrade.
    if is_empty:
        labertasche_db.create_all()


# There is only one user
@loginmgr.user_loader
def user_loader(user_id):
    if user_id != "0":
        return None
    return User(user_id)


# User not authorized
@loginmgr.unauthorized_handler
def login_invalid():
    return redirect(url_for('bp_login.show_login'))


# Enable write-ahead-log for sqlite databases
# noinspection PyUnusedLocal
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if settings.system["database_uri"][0:6] == 'sqlite':
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()
