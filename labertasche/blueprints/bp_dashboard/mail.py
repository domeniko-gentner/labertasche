#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from . import bp_dashboard
from flask import render_template
from flask_login import login_required
from flask_cors import cross_origin
from labertasche.database import labertasche_db as db
from labertasche.models import TEmail


# noinspection PyUnusedLocal
@cross_origin()
@bp_dashboard.route('/manage-mail/')
@bp_dashboard.route('/<project>/manage-mail/')
@login_required
def dashboard_manage_mail(project: str = None):
    """
    Shows the panel to manage email addresses
    :param project: Not used
    :return: The template used to display the route
    """

    addresses = db.session.query(TEmail).all()
    return render_template("manage-mail.html", addresses=addresses)
