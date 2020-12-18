#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from labertasche.database import labertasche_db as db


class TVersion(db.Model):
    # table name
    __tablename__ = "t_version"
    __table_args__ = {'useexisting': True}

    # primary key
    id_version = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # data
    version = db.Column(db.Integer)
