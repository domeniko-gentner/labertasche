#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from labertasche.database import labertasche_db as db
from sqlalchemy import ForeignKey, UniqueConstraint


class TLocation(db.Model):
    # table name
    __tablename__ = "t_location"
    __table_args__ = {'useexisting': True}

    # primary key
    id_location = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # data
    location = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.Integer, ForeignKey('t_projects.id_project'), nullable=False)

    # Unique constraint
    UniqueConstraint('location', 'project_id', name="unique_per_project")
