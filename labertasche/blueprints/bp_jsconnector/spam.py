#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from . import bp_jsconnector
from flask import request, redirect
from flask_login import login_required
from labertasche.database import labertasche_db as db
from labertasche.models import TComments, TEmail
from labertasche.helper import export_location
import re


# @bp_jsconnector.route('/block-mail/<int:location_id>/<int:comment_id>', methods=["GET"])
# @login_required
# def dashboard_review_spam_block_mail(location_id, comment_id):
#     comment = db.session.query(TComments).filter(TComments.comments_id == comment_id).first()
#     if comment:
#         addr = db.session.query(TEmail).filter(TEmail.email == comment.email).first()
#         if addr:
#             setattr(addr, 'is_allowed', False)
#             setattr(addr, 'is_blocked', True)
#         else:
#             new_mail = {
#                 "email": comment.first().email,
#                 "is_allowed": False,
#                 "is_blocked": True
#             }
#             db.session.add(TEmail(**new_mail))
#
#     # Delete all comments made by this mail address
#     db.session.query(TComments).filter(TComments.email == comment.email).delete()
#     db.session.commit()
#
#     url = re.match("^(.*[/])", request.referrer)[0]
#     export_location(location_id)
#     return redirect(f"{url}/{location_id}")
#

# @bp_jsconnector.route('/allow-user/<int:location_id>/<int:comment_id>', methods=["GET"])
# @login_required
# def dashboard_review_spam_allow_user(location_id, comment_id):
#     comment = db.session.query(TComments).filter(TComments.comments_id == comment_id).first()
#     if comment:
#         addr = db.session.query(TEmail).filter(TEmail.email == comment.email).first()
#         if addr:
#             setattr(addr, 'is_allowed', True)
#             setattr(addr, 'is_blocked', False)
#         else:
#             new_mail = {
#                 "email": comment.email,
#                 "is_allowed": True,
#                 "is_blocked": False
#             }
#             db.session.add(TEmail(**new_mail))
#
#     # Allow all comments made by this mail address
#     all_comments = db.session.query(TComments).filter(TComments.email == comment.email).all()
#     if all_comments:
#         for comment in all_comments:
#             setattr(comment, 'is_published', True)
#             setattr(comment, 'is_spam', False)
#
#     db.session.commit()
#     url = re.match("^(.*[/])", request.referrer)[0]
#     export_location(location_id)
#     return redirect(f"{url}/{location_id}")
