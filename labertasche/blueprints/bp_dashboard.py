#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from flask import Blueprint, render_template, request, redirect
from flask_login import login_required
from labertasche.database import labertasche_db as db
from labertasche.models import TLocation, TComments, TEmail
from labertasche.helper import dates_of_the_week, export_location
from sqlalchemy import func
import re

# Blueprint
bp_dashboard = Blueprint("bp_dashboard", __name__, url_prefix='/dashboard')


@bp_dashboard.route('/')
@login_required
def dashboard_index():
    dates = dates_of_the_week()
    spam = list()
    published = list()
    unpublished = list()
    for each in dates:
        spam_comments = db.session.query(TComments).filter(func.DATE(TComments.created_on) == each.date())\
                                                   .filter(TComments.is_spam == True).all()

        pub_comments = db.session.query(TComments).filter(func.DATE(TComments.created_on) == each.date()) \
                                                  .filter(TComments.is_spam == False)\
                                                  .filter(TComments.is_published == True).all()

        unpub_comments = db.session.query(TComments).filter(func.DATE(TComments.created_on) == each.date()) \
                                                    .filter(TComments.is_spam == False)\
                                                    .filter(TComments.is_published == False).all()

        published.append(len(pub_comments))
        spam.append(len(spam_comments))
        unpublished.append(len(unpub_comments))

    return render_template('dashboard.html', dates=dates, spam=spam, published=published, unpublished=unpublished)


@bp_dashboard.route('/review-spam/', methods=["POST", "GET"])
@bp_dashboard.route('/review-spam/<int:location>', methods=["POST", "GET"])
@login_required
def dashboard_review_spam(location=None):
    all_locations = db.session.query(TLocation).all()

    # Check post
    if request.method == "POST":
        location = request.form.get('selected_location')

    # no parameters found
    if location is None:
        return render_template("review-spam.html", locations=all_locations, selected=location)

    try:
        if int(location) >= 1:
            spam_comments = db.session.query(TComments).filter(TComments.location_id == location)\
                                                       .filter(TComments.is_spam == True)
            return render_template("review-spam.html", locations=all_locations, selected=location,
                                   spam_comments=spam_comments)
    except ValueError:
        pass

    return render_template("review-spam.html", locations=all_locations, selected=location)


@bp_dashboard.route('/manage-comments/', methods=["POST", "GET"])
@bp_dashboard.route('/manage-comments/<int:location>', methods=["POST", "GET"])
@login_required
def dashboard_manage_regular_comments(location=None):
    all_locations = db.session.query(TLocation).all()

    # Check post
    if request.method == "POST":
        location = request.form.get('selected_location')

    # no parameters found
    if location is None:
        return render_template("manage-comments.html", locations=all_locations, selected=location)

    try:
        if int(location) >= 1:
            spam_comments = db.session.query(TComments).filter(TComments.location_id == location) \
                .filter(TComments.is_spam == False)
            return render_template("manage-comments.html", locations=all_locations, selected=location,
                                   spam_comments=spam_comments)
    except ValueError:
        pass

    return render_template("manage-comments.html", locations=all_locations, selected=location)


@bp_dashboard.route('/manage-mail/')
@login_required
def dashboard_allow_email():
    addresses = db.session.query(TEmail).all()
    return render_template("manage_mail_addresses.html", addresses=addresses)


@bp_dashboard.route('/toggle-mail-allowed/<int:id_email>')
@login_required
def dashboard_allow_email_toggle(id_email):
    address = db.session.query(TEmail).filter(TEmail.id_email == id_email).first()
    if address:
        setattr(address, "is_allowed", (not address.is_allowed))
        setattr(address, "is_blocked", (not address.is_blocked))
        db.session.commit()
    return redirect(request.referrer)


@bp_dashboard.route('/reset-mail-reputation/<int:id_email>')
@login_required
def dashboard_reset_mail_reputation(id_email):
    db.session.query(TEmail).filter(TEmail.id_email == id_email).delete()
    db.session.commit()
    return redirect(request.referrer)


@bp_dashboard.route('/delete-comment/<int:location_id>/<int:comment_id>', methods=['GET'])
@login_required
def dashboard_review_spam_delete_comment(location_id, comment_id):
    comment = db.session.query(TComments).filter(TComments.comments_id == comment_id).first()
    db.session.delete(comment)
    db.session.commit()

    # Remove after last slash, to keep the location but get rid of the comment id
    url = re.match("^(.*[/])", request.referrer)[0]
    export_location(location_id)
    return redirect(f"{url}/{location_id}")


@bp_dashboard.route('/allow-comment/<int:location_id>/<int:comment_id>', methods=['GET'])
@login_required
def dashboard_review_spam_allow_comment(comment_id, location_id):
    comment = db.session.query(TComments).filter(TComments.comments_id == comment_id).first()
    if comment:
        setattr(comment, 'is_published', True)
        setattr(comment, 'is_spam', False)
        db.session.commit()

    url = re.match("^(.*[/])", request.referrer)[0]
    export_location(location_id)
    return redirect(f"{url}/{location_id}")


@bp_dashboard.route('/block-mail/<int:location_id>/<int:comment_id>', methods=["GET"])
@login_required
def dashboard_review_spam_block_mail(location_id, comment_id):
    comment = db.session.query(TComments).filter(TComments.comments_id == comment_id).first()
    if comment:
        mail = db.session.query(TEmail).filter(TEmail.email == comment.email).first()
        if mail:
            setattr(mail, 'is_allowed', False)
            setattr(mail, 'is_blocked', True)
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

    url = re.match("^(.*[/])", request.referrer)[0]
    export_location(location_id)
    return redirect(f"{url}/{location_id}")


@bp_dashboard.route('/allow-user/<int:location_id>/<int:comment_id>', methods=["GET"])
@login_required
def dashboard_review_spam_allow_user(location_id, comment_id):
    comment = db.session.query(TComments).filter(TComments.comments_id == comment_id).first()
    if comment:
        mail = db.session.query(TEmail).filter(TEmail.email == comment.email).first()
        if mail:
            setattr(mail, 'is_allowed', True)
            setattr(mail, 'is_blocked', False)
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
    url = re.match("^(.*[/])", request.referrer)[0]
    export_location(location_id)
    return redirect(f"{url}/{location_id}")
