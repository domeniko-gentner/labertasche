#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
# noinspection PyProtectedMember
from sqlalchemy.engine import Engine
from logging import getLogger, ERROR as LOGGING_ERROR
from flask import Flask, redirect, url_for, request
from flask_cors import CORS
from sqlalchemy import event, inspect
from labertasche.settings import Settings, Secret
from labertasche.database import labertasche_db
from labertasche.language import Language
from labertasche.blueprints import bp_comments, bp_login, bp_dashboard, bp_jsconnector, bp_dbupgrades
from labertasche.helper import User
from flask_login import LoginManager
from datetime import timedelta

# Load settings
settings = Settings()
secret = Secret()

# Flask App
laberflask = Flask(__name__)
laberflask.config.update(dict(
    SESSION_COOKIE_DOMAIN=settings.cookie_domain,
    SESSION_COOKIE_SECURE=settings.cookie_secure,
    REMEMBER_COOKIE_SECURE=settings.cookie_secure,
    REMEMBER_COOKIE_DURATION=timedelta(days=7),
    REMEMBER_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST=True,
    DEBUG=settings.debug,
    SECRET_KEY=secret.key,
    TEMPLATES_AUTO_RELOAD=settings.debug,
    SQLALCHEMY_DATABASE_URI=settings.database_uri,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    JSON_AS_ASCII=False
))

# Mark secret for deletion
del secret

# Import blueprints
laberflask.register_blueprint(bp_comments)
laberflask.register_blueprint(bp_dashboard)
laberflask.register_blueprint(bp_login)
laberflask.register_blueprint(bp_jsconnector)
laberflask.register_blueprint(bp_dbupgrades)

# Disable Werkzeug's verbosity during development
log = getLogger('werkzeug')
log.setLevel(LOGGING_ERROR)

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


# CORS
cors = CORS(laberflask)


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
    if settings.database_uri[0:6] == 'sqlite':
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()


# Inject i18n dictionaries into all templates
@laberflask.context_processor
def inject_language():
    lang = Language(request)
    return {"i18n": lang.i18n}


@laberflask.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response
