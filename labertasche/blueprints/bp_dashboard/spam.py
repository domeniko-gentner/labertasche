#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from . import bp_dashboard
from flask import render_template, request, redirect, url_for
from flask_login import login_required
from flask_cors import cross_origin
from labertasche.database import labertasche_db as db
from labertasche.models import TLocation, TComments
from labertasche.helper import export_location, get_id_from_project_name


@cross_origin()
@bp_dashboard.route('<project>/manage-spam/', methods=["GET"])
@login_required
def dashboard_review_spam(project: str):
    """
    Shows the manage spam template
    :param project: The project used for displaying data
    :return: The template to display for this rouet
    """
    location_id = 0
    proj_id = get_id_from_project_name(project)
    all_locations = db.session.query(TLocation).filter(TLocation.project_id == proj_id).all()

    # Project does not exist, error code is used by Javascript, not Flask
    if proj_id == -1:
        return redirect(url_for("bp_dashboard.dashboard_project_list", error=404))

    if request.args.get('location'):
        location_id = request.args.get('location')

    # no parameters found
    if location_id is None:
        return render_template("manage-comments.html", locations=all_locations,
                               selected=location_id, title="Review Spam", action="spam")

    try:
        if int(location_id) >= 1:
            spam_comments = db.session.query(TComments) \
                .filter(TComments.project_id == proj_id) \
                .filter(TComments.location_id == location_id) \
                .filter(TComments.is_spam == True)

            return render_template("manage-comments.html", locations=all_locations, selected=location_id,
                                   spam_comments=spam_comments, project=project, title="Review Spam", action="spam")
    except ValueError:
        pass

    export_location(location_id)
    return render_template("manage-comments.html", locations=all_locations,
                           selected=location_id, project=project, title="Review Spam", action="spam")

