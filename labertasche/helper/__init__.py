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
from hashlib import md5
from flask_login import UserMixin
from pathlib import Path
from sys import stderr
from re import match as re_match
from labertasche.models import TLocation, TComments, TProjects
from labertasche.database import labertasche_db as db


class User(UserMixin):
    """
    Class for flask-login, which represents a user
    """
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
    except json.JSONDecodeError:
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
def check_gravatar(email: str, name: str):
    """
    Builds the gravatar email hash, which uses md5.
    You may use ?size=128 for example to dictate size in the final template.
    :param email: the email to use for the hash
    :param name: The project name
    :return: the gravatar url of the image
    """
    from requests import get
    project = db.session.query(TProjects).filter(TProjects.name == name).first()
    gravatar_hash = md5(email.strip().lower().encode("utf8")).hexdigest()

    if project.gravatar_cache:
        url = f"https://www.gravatar.com/avatar/{gravatar_hash}?s={project.gravatar_size}"
        response = get(url)
        if response.ok:
            outfile = Path(f"{project.gravatar_cache_dir}/{gravatar_hash}.jpg")
            with outfile.open('wb') as fp:
                response.raw.decode_content = True
                for chunk in response:
                    fp.write(chunk)
    return gravatar_hash


def export_location(location_id: int) -> bool:
    """
        Exports the comments for the location after the comment was accepted
        :param location_id: The id of the store location to export
    """
    try:
        # flush before query
        db.session.flush()

        # Query
        location = db.session.query(TLocation).filter(TLocation.id_location == location_id).first()

        if location:
            comments = db.session.query(TComments).filter(TComments.is_spam != True) \
                                                  .filter(TComments.is_published == True) \
                                                  .filter(TComments.location_id == location.id_location) \
                                                  .filter(TProjects.id_project == location.project_id) \
                                                  .all()
            project = db.session.query(TProjects).filter(TProjects.id_project == location.project_id).first()

            # Removes the last slash
            path_loc = re_match(".*(?=/)", location.location)[0]

            # Construct export path
            jsonfile = Path(f"{project.output}/{path_loc}.json").absolute()
            folder = jsonfile.parents[0]

            # If there are no comments, do not export and remove empty file.
            # The database is the point of trust.
            if len(comments) == 0:
                jsonfile.unlink(missing_ok=True)
                return True

            bundle = {
                "comments": [],
                "replies": []
            }
            for comment in comments:
                if comment.replied_to is not None:
                    bundle["replies"].append(alchemy_query_to_dict(comment))
                    continue
                bundle['comments'].append(alchemy_query_to_dict(comment))

            # Create folder if not exists and write file
            folder.mkdir(parents=True, exist_ok=True)
            with jsonfile.open('w') as fp:
                json.dump(bundle, fp)

            return True

    except Exception as e:
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


def get_id_from_project_name(name: str) -> int:
    """
    Returns the id of a project name
    :param name: The display name of the project
    :return: the ID of the project
    """
    proj = db.session.query(TProjects).filter(TProjects.name == name).first()

    if proj is None:
        return -1

    return proj.id_project
