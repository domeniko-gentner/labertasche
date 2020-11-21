#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from labertasche.database import labertasche_db as db


class TEmail(db.Model):
    # Table name
    __tablename__ = 't_email'
    __table_args__ = {'useexisting': True}

    # primary key
    id_email = db.Column(db.Integer, primary_key=True)

    # data
    email = db.Column(db.Integer, unique=True)
    is_blocked = db.Column(db.Boolean)
    is_allowed = db.Column(db.Boolean)
