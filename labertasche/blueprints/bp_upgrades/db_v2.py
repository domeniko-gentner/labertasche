#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from . import bp_dbupgrades
from flask_cors import cross_origin
from flask_login import login_required
from flask import render_template, jsonify, make_response, redirect, url_for, current_app
from pathlib import Path
from labertasche.database import labertasche_db as db
from labertasche.models import TProjects, TComments, TLocation, TEmail, TVersion
from labertasche.settings import LegacySettings
from json import dump, load
from shutil import copy, make_archive
from re import search
from secrets import compare_digest
from datetime import datetime


def get_backup_folder() -> Path:
    path = Path(current_app.root_path)
    path = path / "backup" / "v1"
    return path


@cross_origin()
@bp_dbupgrades.route('/db_v2/')
@login_required
def upgrade_db_to_v2():
    # TODO: Check if db has already been upgraded
    status = False
    try:
        version = db.session.query(TVersion).first()
        if version:
            status = True
            return redirect(url_for('bp_dashboard.dashboard_project_list'))

    except Exception as e:
        print(e.__class__)
        pass

    return render_template("db-upgrades.html", title="DB upgrade V1 to V2",
                           prev_version=1, new_version=2, status=status)


@cross_origin()
@bp_dbupgrades.route('/db_v2/backup/', methods=['GET'])
@login_required
def upgrade_db_to_v2_backup():
    path = get_backup_folder()
    # Create path for backup
    try:
        if not path.exists():
            path.mkdir(mode=777, exist_ok=True, parents=True)
    except OSError as e:
        return make_response(jsonify(status='exception', msg=str(e)), 400)

    return make_response(jsonify(status="ok"), 200)


@cross_origin()
@bp_dbupgrades.route('/db_v2/export/')
@login_required
def upgrade_db_to_v2_export():
    path = get_backup_folder()

    # make sure nothing is pending
    db.session.commit()

    # Export tables
    t_locations = db.session.query(TLocation.id_location, TLocation.location).all()
    t_emails = db.session.query(TEmail.id_email, TEmail.email, TEmail.is_allowed, TEmail.is_blocked).all()
    t_comments = db.session.query(TComments.comments_id, TComments.location_id, TComments.email,
                                  TComments.content, TComments.created_on, TComments.is_published,
                                  TComments.is_spam, TComments.spam_score, TComments.replied_to,
                                  TComments.confirmation, TComments.deletion, TComments.gravatar).all()

    locations = []
    for loc in t_locations:
        locations.append({
            "id_location": loc.id_location,
            "location": loc.location
        })

    emails = []
    for mail in t_emails:
        emails.append({
            "id_email": mail.id_email,
            "email": mail.email,
            "is_allowed": mail.is_allowed,
            "is_blocked": mail.is_blocked
        })

    comments = []
    for comment in t_comments:
        comments.append({
            "comments_id": comment.comments_id,
            "location_id": comment.location_id,
            "email": comment.email,
            "content": comment.content,
            "created_on": f"{comment.created_on.__str__()}",
            "is_published": comment.is_published,
            "is_spam": comment.is_spam,
            "spam_score": comment.spam_score,
            "replied_to": comment.replied_to,
            "confirmation": comment.confirmation,
            "deletion": comment.deletion,
            "gravatar": comment.gravatar
        })

    # Output jsons
    try:
        p_export_location = path / "locations.json"
        with p_export_location.open('w') as fp:
            dump(locations, fp, indent=4, sort_keys=True)

        p_export_mail = path / "emails.json"
        with p_export_mail.open('w') as fp:
            dump(emails, fp, indent=4, sort_keys=True)

        p_export_comments = path / "comments.json"
        with p_export_comments.open('w') as fp:
            dump(comments, fp, indent=4, sort_keys=True)

    except Exception as e:
        return make_response(jsonify(status='exception-write-json', msg=str(e)), 400)

    # Copy database
    try:
        settings = LegacySettings(True)
        db_uri = settings.system['database_uri']
        if compare_digest(db_uri[0:6], "sqlite"):
            m = search("([/]{3})(.*)", db_uri)
            new_db = get_backup_folder() / "labertasche.db"
            old_db = Path(current_app.root_path)
            old_db = old_db / m.group(2)
            copy(old_db.absolute(), new_db.absolute())
    except Exception as e:
        return make_response(jsonify(status='exception-copy-db', msg=str(e)), 400)

    make_archive(path, "zip", path)

    return make_response(jsonify(status='ok'), 200)


@cross_origin()
@bp_dbupgrades.route('/db_v2/recreate/')
@login_required
def upgrade_db_to_v2_recreate():
    try:
        db.drop_all()
        db.session.flush()
        db.session.commit()
        db.create_all()
    except Exception as e:
        return make_response(jsonify(status='exception', msg=str(e)), 400)

    return make_response(jsonify(status='ok'), 200)


@cross_origin()
@bp_dbupgrades.route('/db_v2/import/')
@login_required
def upgrade_db_to_v2_import():
    path = get_backup_folder()
    settings = LegacySettings(True)

    try:
        # load location
        p_loc = (path / 'locations.json').absolute()
        with p_loc.open('r') as fp:
            locations = load(fp)

        # load mails
        m_loc = (path / 'emails.json').absolute()
        with m_loc.open('r') as fp:
            mails = load(fp)

        # load comments
        c_loc = (path / 'comments.json').absolute()
        with c_loc.open('r') as fp:
            comments = load(fp)

    except FileNotFoundError as e:
        return make_response(jsonify(status='exception-filenotfound', msg=str(e)), 400)

    # Create project
    default_project = {
        "id_project": 1,
        "name": "default",
        "blogurl": settings.system['blog_url'],
        "output": settings.system['output'],
        "sendotp": settings.system['send_otp_to_publish'],
        "gravatar_cache": settings.gravatar['cache'],
        "gravatar_cache_dir": settings.gravatar['static_dir'],
        "gravatar_size": settings.gravatar['size'],
        "addon_smileys": settings.addons['smileys']
    }

    # Create db version, so we can track it in the future
    version = {
        "id_version": 1,
        "version": 2
    }

    try:
        # Add to db
        db.session.add(TVersion(**version))
        db.session.add(TProjects(**default_project))

        # walk json and readd to database with project set to project 1
        for each in mails:
            each.update({'project_id': 1})
            db.session.add(TEmail(**each))

        for each in locations:
            each.update({'project_id': 1})
            db.session.add(TLocation(**each))

        for each in comments:
            each.update({'project_id': 1})
            dt = datetime.fromisoformat(each['created_on'])
            each.update({'created_on': dt})
            db.session.add(TComments(**each))

        # Commit
        db.session.commit()
        db.session.flush()
    except Exception as e:
        return make_response(jsonify(status='exception-database', msg=str(e)), 400)

    return make_response(jsonify(status='ok'), 200)
