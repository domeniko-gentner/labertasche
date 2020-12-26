#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from . import bp_dashboard
from flask import render_template, redirect, url_for, request
from flask_login import login_required
from flask_cors import cross_origin
from sqlalchemy import func
from sqlalchemy.exc import OperationalError
from labertasche.database import labertasche_db as db
from labertasche.models import TComments, TProjects
from labertasche.helper import get_id_from_project_name, dates_of_the_week


@cross_origin
@bp_dashboard.route("/")
@login_required
def dashboard_project_list():
    """
    Displays an overview of all projects.
    :return: The overview template.
    """
    try:
        t_projects = db.session.query(TProjects).all()
    except OperationalError:
        # Database not up-to-date
        return redirect(url_for('bp_dbupgrades.upgrade_db_to_v2'))

    projects = list()
    for each in t_projects:
        comments = db.session.query(TComments).filter(TComments.project_id == each.id_project) \
            .filter(TComments.is_published == True) \
            .filter(TComments.is_spam == False).count()
        unpub_comments = db.session.query(TComments).filter(TComments.project_id == each.id_project) \
            .filter(TComments.is_spam == False) \
            .filter(TComments.is_published == False).count()
        spam = db.session.query(TComments).filter(TComments.project_id == each.id_project) \
            .filter(TComments.is_spam == True).count()

        projects.append(dict({
            "id_project": each.id_project,
            "name": each.name,
            "total_comments": comments,
            "total_spam": spam,
            "total_unpublished": unpub_comments
        }))
    return render_template('project-list.html', projects=projects)


@cross_origin
@bp_dashboard.route('/<project>/')
@login_required
def dashboard_project_stats(project: str):
    """
    Displays the project dashboard

    :param project: The project to show
    :return: The template for the route
    """
    proj_id = get_id_from_project_name(project)

    # Project does not exist, error code is used by Javascript, not Flask
    if proj_id == -1:
        return redirect(url_for("bp_dashboard.dashboard_project_list", error=404))

    # Total graphs
    total_spam = db.session.query(TComments).filter(TComments.is_spam == True).count()

    total_comments = db.session.query(TComments) \
                               .filter(TComments.is_spam == False)\
                               .filter(TComments.is_published == True).count()

    total_unpublished = db.session.query(TComments).filter(TComments.is_spam == False)\
        .filter(TComments.is_published == False).count()

    # 7 day graph
    dates = dates_of_the_week()
    spam = list()
    published = list()
    unpublished = list()
    for each in dates:
        spam_comments = db.session.query(TComments).filter(TComments.project_id == proj_id) \
            .filter(func.DATE(TComments.created_on) == each.date()) \
            .filter(TComments.is_spam == True).all()

        pub_comments = db.session.query(TComments).filter(func.DATE(TComments.created_on) == each.date()) \
            .filter(TComments.project_id == proj_id) \
            .filter(TComments.is_spam == False) \
            .filter(TComments.is_published == True).all()

        unpub_comments = db.session.query(TComments).filter(func.DATE(TComments.created_on) == each.date()) \
            .filter(TComments.project_id == proj_id) \
            .filter(TComments.is_spam == False) \
            .filter(TComments.is_published == False).all()

        published.append(len(pub_comments))
        spam.append(len(spam_comments))
        unpublished.append(len(unpub_comments))

    return render_template('project-stats.html', dates=dates, spam=spam, project=project,
                           published=published, unpublished=unpublished,
                           total_spam=total_spam, total_comments=total_comments,
                           total_unpublished=total_unpublished)

