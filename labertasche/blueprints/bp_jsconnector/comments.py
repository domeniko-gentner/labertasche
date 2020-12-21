#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from . import bp_jsconnector
from flask import request, redirect, make_response, jsonify
from flask_login import login_required
from flask_cors import cross_origin
from labertasche.database import labertasche_db as db
from labertasche.helper import export_location, get_id_from_project_name
from labertasche.models import TComments, TEmail, TLocation

# This file contains the routes for the manage comments menu point.
# They are called via GET


@cross_origin()
@bp_jsconnector.route('/comment-delete/<int:comment_id>', methods=['GET'])
@login_required
def api_comments_delete_comment(comment_id):
    db.session.query(TComments).filter(TComments.comments_id == comment_id).delete()
    db.session.commit()

    # Get location id from get params
    location_id = request.args.get('location')

    export_location(location_id)
    return redirect(request.referrer)


@cross_origin()
@bp_jsconnector.route('/comment-allow/<int:comment_id>', methods=['GET'])
@login_required
def api_comment_allow_comment(comment_id):
    comment = db.session.query(TComments).filter(TComments.comments_id == comment_id).first()
    if comment:
        setattr(comment, 'is_published', True)
        setattr(comment, 'is_spam', False)
        db.session.commit()

    # Get location id from get params
    location_id = request.args.get('location')

    export_location(location_id)
    return redirect(request.referrer)


@cross_origin()
@bp_jsconnector.route('/comment-allow-user/<int:comment_id>', methods=["GET"])
@login_required
def api_comment_allow_user(comment_id):
    comment = db.session.query(TComments).filter(TComments.comments_id == comment_id).first()
    if comment:
        addr = db.session.query(TEmail).filter(TEmail.email == comment.email).first()
        if addr:
            setattr(addr, 'is_allowed', True)
            setattr(addr, 'is_blocked', False)
        else:
            new_mail = {
                "email": comment.email,
                "is_allowed": True,
                "is_blocked": False
            }
            db.session.add(TEmail(**new_mail))

    # Allow all comments made by this mail address
    all_comments = db.session.query(TComments).filter(TComments.email == comment.email).all()
    if all_comments:
        for comment in all_comments:
            setattr(comment, 'is_published', True)
            setattr(comment, 'is_spam', False)

    db.session.commit()

    # Get location id from get params
    location_id = request.args.get('location')

    export_location(location_id)
    return redirect(request.referrer)


@cross_origin()
@bp_jsconnector.route('/comment-block-mail/<int:comment_id>', methods=["GET"])
@login_required
def api_comment_block_mail(comment_id):
    comment = db.session.query(TComments).filter(TComments.comments_id == comment_id).first()
    if comment:
        addr = db.session.query(TEmail).filter(TEmail.email == comment.email).first()
        if addr:
            setattr(addr, 'is_allowed', False)
            setattr(addr, 'is_blocked', True)
        else:
            new_mail = {
                "email": comment.first().email,
                "is_allowed": False,
                "is_blocked": True
            }
            db.session.add(TEmail(**new_mail))

    # Delete all comments made by this mail address
    db.session.query(TComments).filter(TComments.email == comment.email).delete()
    db.session.commit()

    # Get location id from get params
    location_id = request.args.get('location')

    export_location(location_id)
    return redirect(request.referrer)


@cross_origin()
@bp_jsconnector.route('/comment-export-all/<name>', methods=["GET"])
@login_required
def api_export_all_by_project(name):
    proj_id = get_id_from_project_name(name)
    if proj_id == -1:
        return make_response(jsonify(status='not-found'), 400)

    try:
        locations = db.session.query(TLocation).all()
        for each in locations:
            export_location(each.id_location)
    except Exception as e:
        return make_response(jsonify(status='sql-error', msg=str(e)), 400)

    return make_response(jsonify(status='ok'), 200)
