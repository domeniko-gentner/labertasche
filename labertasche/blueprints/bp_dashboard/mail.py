#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from . import bp_dashboard
from flask import render_template, redirect, url_for
from flask_login import login_required
from flask_cors import cross_origin
from labertasche.database import labertasche_db as db
from labertasche.models import TEmail
from labertasche.helper import get_id_from_project_name


@cross_origin()
@bp_dashboard.route('<project>/manage-mail/')
@login_required
def dashboard_manage_mail(project: str):
    """
    Shows the panel to manage email addresses
    :param project: The project name to manage
    :return: The template used to display the route
    """
    proj_id = get_id_from_project_name(project)

    # Project does not exist, error code is used by Javascript, not Flask
    if proj_id == -1:
        return redirect(url_for("bp_dashboard.dashboard_project_list", error=404))

    addresses = db.session.query(TEmail).filter(TEmail.project_id == proj_id).all()
    return render_template("manage-mail.html", addresses=addresses, project=project)
