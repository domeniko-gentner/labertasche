#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from labertasche.database import labertasche_db as db


class TProjects(db.Model):
    # table name
    __tablename__ = "t_projects"
    __table_args__ = {'useexisting': True}

    # primary key
    id_project = db.Column(db.Integer, primary_key=True)

    # data
    name = db.Column(db.Text, nullable=True, unique=True)
