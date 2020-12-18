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
import re


@cross_origin()
@bp_jsconnector.route("/project/new", methods=['POST'])
@login_required
def api_create_project():
    """
    Called on dashboard project overview to create a new project.

    :return: A string with an error code and 'ok' as string on success.
    """
    # TODO: Project name exists?
    name = request.json['name']

    if not len(name):
        return make_response(jsonify(status='too-short'), 400)
    if not re.match('^\\w+$', name):
        return make_response(jsonify(status='invalid-name'), 400)

    proj = TProjects(name=name)
    db.session.add(proj)
    db.session.commit()

    return make_response(jsonify(status='ok'), 200)


@cross_origin()
@bp_jsconnector.route('project/edit/<name>', methods=['POST'])
@login_required
def api_edit_project_name(name: str):
    """
    Renames the project.
    :param name:
    :return: A string with an error code and 'ok' as string on success.
    """
    # TODO: Project name exists?
    new_name = request.json['name']

    if not len(new_name):
        return make_response(jsonify(status='too-short'), 400)
    if not re.match('^\\w+$', new_name):
        return make_response(jsonify(status='invalid-name'), 400)

    proj_id = get_id_from_project_name(name)
    project = db.session.query(TProjects).filter(TProjects.id_project == proj_id)
    setattr(project, 'name', new_name)
    db.session.upate(project)
    db.session.commit()

    return make_response(jsonify(status='ok'), 200)


@cross_origin()
@bp_jsconnector.route('project/delete/<project>', methods=['GET'])
@login_required
def api_delete_project(project: str):
    """
    Deletes a project from the database and all associated data

    :param project: The name of the project
    :return: A string with an error code and 'ok' as string on success.
    """
    proj_id = get_id_from_project_name(project)
    if proj_id == -1:
        return make_response(jsonify(status='not-found'), 400)

    # noinspection PyBroadException
    try:
        db.session.query(TComments).filter(TComments.project_id == proj_id).delete()
        db.session.query(TLocation).filter(TLocation.project_id == proj_id).delete()
        db.session.query(TEmail).filter(TEmail.project_id == proj_id).delete()
        db.session.query(TProjects).filter(TProjects.id_project == proj_id).delete()
        db.session.commit()
        db.session.flush()
    except Exception:
        return make_response(jsonify(status='exception'), 400)

    return make_response(jsonify(status='ok'), 200)
