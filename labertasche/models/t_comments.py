#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from labertasche.database import labertasche_db as db
from sqlalchemy import ForeignKey


class TComments(db.Model):
    # table name
    __tablename__ = "t_comments"
    __table_args__ = {'useexisting': True}

    # primary key
    comments_id = db.Column(db.Integer, primary_key=True)

    # foreign keys
    location_id = db.Column(db.Integer, ForeignKey('t_location.id_location'), nullable=False)

    # data
    email = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False, unique=True)
    created_on = db.Column(db.DateTime, nullable=False)
    is_published = db.Column(db.Boolean, nullable=False)
    is_spam = db.Column(db.Boolean, nullable=False)
    spam_score = db.Column(db.Float, nullable=False)
    replied_to = db.Column(db.Integer, ForeignKey('t_comments.comments_id'), nullable=True, default=None)
    confirmation = db.Column(db.Text, nullable=True)
    deletion = db.Column(db.Text, nullable=True)
    gravatar = db.Column(db.Text, nullable=True)
    project_id = db.Column(db.Integer, ForeignKey('t_projects.id_project'), nullable=False)
