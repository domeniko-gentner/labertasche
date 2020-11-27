#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
import datetime
import json
from labertasche.models import TLocation, TComments
from labertasche.settings import Settings
from labertasche.database import labertasche_db as db
from functools import wraps
from hashlib import md5
from flask import request
from flask_login import UserMixin
from secrets import compare_digest
from pathlib import Path
from sys import stderr
from re import match as re_match
import requests


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


def is_valid_json(j):
    """
    Tries to load the json to test if it is valid.

    :param j: The json to test.
    :return: True if the json is valid, False on any exception.
    """
    try:
        json.dumps(j)
        return True
    except json.JSONDecodeError as e:
        print("not valid json")
        return False


def default_timestamp():
    """Timestamp used by the project to ensure consistency"""
    date = datetime.datetime.now().replace(microsecond=0)
    return date


def time_to_js(obj):
    """"
    Returns a timestring readable by Javascript
    """
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()


def alchemy_query_to_dict(obj):
    """
    Used when exporting the data. It truncates the mail, removes the T from the date string, etc.

    :param obj: A single query item from sqlalchemy.
    :return: a dict with the query
    """
    no_mail = re_match("^.*[@]", obj.email)[0]
    result = {
        "comment_id": obj.comments_id,
        "email": no_mail,
        "content": obj.content,
        "created_on": time_to_js(obj.created_on).replace("T", " "),
        "replied_to": obj.replied_to,
        "gravatar": obj.gravatar
    }
    return dict(result)


# Come on, it's  a mail hash, don't complain
# noinspection InsecureHash
def check_gravatar(email: str):
    """
    Builds the gravatar email hash, which uses md5.
    You may use ?size=128 for example to dictate size in the final template.
    :param email: the email to use for the hash
    :return: the gravatar url of the image
    """
    settings = Settings()
    options = settings.gravatar
    gravatar_hash = md5(email.strip().lower().encode("utf8")).hexdigest()
    if options['cache']:
        url = f"https://www.gravatar.com/avatar/{gravatar_hash}?s={options['size']}"
        response = requests.get(url)
        if response.ok:
            outfile = Path(f"{options['static_dir']}/{gravatar_hash}.jpg")
            if not outfile.exists():
                with outfile.open('wb') as fp:
                    response.raw.decode_content = True
                    for chunk in response:
                        fp.write(chunk)

    return gravatar_hash


def check_auth(username: str, password: str):
    """
    Compares username and password from the settings file in a safe way.
    Direct string comparison is vulnerable to timing attacks
    https://sqreen.github.io/DevelopersSecurityBestPractices/timing-attack/python
    :param username: username entered by the user
    :param password: password entered by the user
    :return: True if equal, False if not
    """
    settings = Settings()
    if compare_digest(username, settings.dashboard['username']) and \
            compare_digest(password, settings.dashboard['password']):
        return True
    return False


def basic_login_required(f):
    """
    Decorator for basic auth
    """
    @wraps(f)
    def wrapped_view(**kwargs):
        auth = request.authorization
        if not (auth and check_auth(auth.username, auth.password)):
            return ('Unauthorized', 401, {
                'WWW-Authenticate': 'Basic realm="Login Required"'
            })
        return f(**kwargs)
    return wrapped_view


def export_location(location_id: int) -> bool:
    """
        Exports the comments for the location after the comment was accepted
        :param location_id: The id of the store location to export
    """
    try:
        # flush before query
        db.session.flush()

        # Query
        loc_query = db.session.query(TLocation).filter(TLocation.id_location == location_id).first()

        if loc_query:
            print(f"has loc_query")
            comments = db.session.query(TComments).filter(TComments.is_spam != True) \
                .filter(TComments.is_published == True) \
                .filter(TComments.location_id == loc_query.id_location) \
                .filter(TComments.replied_to == None)

            bundle = {
                "comments": []
            }
            for comment in comments:
                bundle['comments'].append(alchemy_query_to_dict(comment))

            path_loc = re_match(".*(?=/)", loc_query.location)[0]

            system = Settings().system
            out = Path(f"{system['output']}/{path_loc}.json")
            out = out.absolute()
            print(out)
            folder = out.parents[0]
            folder.mkdir(parents=True, exist_ok=True)
            with out.open('w') as fp:
                json.dump(bundle, fp)
                print(bundle)

            return True

    except Exception as e:
        # mail(f"export_comments has thrown an error: {str(e)}")
        print(e, file=stderr)
        return False


def dates_of_the_week():
    """
    Finds all dates of this week and returns them as a list,
    going from midnight on monday to sunday 1 second before midnight
    :return: A list containing the dates
    """
    date_list = list()
    now = datetime.datetime.now()
    monday = now - datetime.timedelta(days=now.weekday(), hours=now.hour, minutes=now.minute, seconds=now.second,
                                      microseconds=now.microsecond)
    date_list.append(monday)
    for each in range(1, 6):
        monday = monday + datetime.timedelta(days=1)
        date_list.append(monday)
    date_list.append((monday + datetime.timedelta(days=1, hours=23, minutes=59, seconds=59)))
    return date_list
