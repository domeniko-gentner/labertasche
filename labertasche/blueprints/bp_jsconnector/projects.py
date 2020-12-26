#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from . import bp_jsconnector
from flask import request, make_response, jsonify
from flask_login import login_required
from flask_cors import cross_origin
from labertasche.database import labertasche_db as db
from labertasche.helper import get_id_from_project_name
from labertasche.models import TProjects, TComments, TEmail, TLocation
from validators import url as validate_url
from pathlib import Path
from secrets import compare_digest
import re


def validate_project(project, is_edit=False):
    """
    Validates important bits of a project database entry

    :param project: The json from the request, containing the data for a project.
    :param is_edit: If we are updating the database, we need to know, so we don't check for dupes on urls.
    :return: A response with the error or None if the project is valid.
    """
    # Validate length
    if not len(project['name']) and \
            not len(project['blogurl']) and \
            not len(project['output']):
        return make_response(jsonify(status='too-short'), 400)

    # Validate project name
    if not re.match('^\\w+$', project['name']):
        return make_response(jsonify(status='invalid-project-name'), 400)

    # Check if project name already exists
    name_check = db.session.query(TProjects.name).filter(TProjects.name == project['name']).first()
    if name_check and not is_edit:
        return make_response(jsonify(status='project-exists'), 400)

    # Validate existing only if we are not editing
    url_exists = False
    if not is_edit:
        url_exists = db.session.query(TProjects.blogurl).filter(TProjects.blogurl == project['blogurl']).first()

    if not validate_url(project['blogurl']) or url_exists:
        return make_response(jsonify(status='invalid-blog-url'), 400)

    # Validate output path
    output = Path(project['output']).absolute()
    # The second check is needed, since javascript is passing an empty string instead of
    # null. For some reason, this makes SQLAlchemy accept the data and commit it to the db
    # without exception. This check prevents this issue from happening.
    if not output.exists() or len(project['output'].strip()) == 0:
        return make_response(jsonify(status='invalid-path-output'), 400)

    # Validate cache path, if caching is enabled
    if project['gravatar_cache']:
        cache = Path(project['gravatar_cache_dir']).absolute()
        if not cache.exists() or len(project['gravatar_cache_dir'].strip()) == 0:
            return make_response(jsonify(status='invalid-path-cache'), 400)

    return None


@cross_origin()
@bp_jsconnector.route("/project/new", methods=['POST'])
@login_required
def api_create_project():
    """
    Called on dashboard project overview to create a new project.

    :return: A string with an error code and 'ok' as string on success.
    """
    response = validate_project(request.json)
    if response is not None:
        return response

    try:
        new_project = request.json
        # Remove trailing slash
        if compare_digest(new_project['blogurl'][-1], '/'):
            new_project['blogurl'] = new_project['blogurl'][:-1]

        db.session.add(TProjects(**new_project))
        db.session.commit()
    except Exception as e:
        print(str(e))
        db.session.rollback()
        return make_response(jsonify(status='exception', msg=str(e)), 500)

    return make_response(jsonify(status='ok'), 200)


@cross_origin()
@bp_jsconnector.route('/project/edit/<name>', methods=['POST'])
@login_required
def api_edit_project_name(name: str):
    """
    Renames the project.
    :param name: The previous name of the project to edit, must exist
    :return: A string with an error code and 'ok' as string on success.
    """
    response = validate_project(request.json, is_edit=True)
    if response is not None:
        return response

    try:
        project = db.session.query(TProjects).filter(TProjects.name == name).first()

        project_json = request.json
        # Remove trailing slash to streamline it
        if compare_digest(project_json['blogurl'][-1], '/'):
            setattr(project, "blogurl", project_json['blogurl'][:-1].strip())

        setattr(project, "id_project", project.id_project)
        setattr(project, "name", project_json['name'])
        setattr(project, "output", project_json['output'].strip())
        setattr(project, "sendotp", project_json['sendotp'])
        setattr(project, "gravatar_cache", project_json['gravatar_cache'])
        setattr(project, "gravatar_cache_dir", project_json['gravatar_cache_dir'])
        setattr(project, "gravatar_size", project_json['gravatar_size'])
        setattr(project, "addon_smileys", project_json['addon_smileys'])
        db.session.commit()
    except Exception as e:
        print(str(e))
        return make_response(jsonify(status='exception', msg=str(e)), 500)

    return make_response(jsonify(status='ok'), 200)


@cross_origin()
@bp_jsconnector.route('/project/delete/<name>', methods=['GET'])
@login_required
def api_delete_project(name: str):
    """
    Deletes a project from the database and all associated data

    :param name: The name of the project
    :return: A string with an error code and 'ok' as string on success.
    """
    proj_id = get_id_from_project_name(name)
    if proj_id == -1:
        return make_response(jsonify(status='not-found'), 400)

    # noinspection PyBroadException
    try:
        db.session.query(TComments).filter(TComments.project_id == proj_id).delete()
        db.session.query(TLocation).filter(TLocation.project_id == proj_id).delete()
        db.session.query(TProjects).filter(TProjects.id_project == proj_id).delete()
        db.session.commit()
        db.session.flush()
    except Exception:
        return make_response(jsonify(status='exception'), 400)

    return make_response(jsonify(status='ok'), 200)


@cross_origin()
@bp_jsconnector.route('/project/exists/<name>', methods=['GET'])
@login_required
def api_project_exists(name: str):
    proj_id = get_id_from_project_name(name)
    if proj_id == -1:
        return make_response(jsonify(status='not-found'), 200)
    return make_response(jsonify(status='ok'), 200)


@cross_origin()
@bp_jsconnector.route('/project/get/<name>', methods=['GET'])
@login_required
def api_project_get_data(name: str):
    project = db.session.query(TProjects).filter(TProjects.name == name).first()
    if project:
        return make_response(jsonify(status='ok',
                                     id_project=project.id_project,
                                     name=project.name,
                                     blogurl=project.blogurl,
                                     output=project.output,
                                     sendotp=project.sendotp,
                                     gravatar_cache=project.gravatar_cache,
                                     gravatar_cache_dir=project.gravatar_cache_dir,
                                     gravatar_size=project.gravatar_size,
                                     addon_smileys=project.addon_smileys), 200)
    else:
        print('400')
        return make_response(jsonify(status='not-found'), 400)
