#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from flask import Blueprint

# Blueprint
bp_dbupgrades = Blueprint("bp_dbupgrades", __name__, url_prefix='/upgrade')

from .db_v2 import upgrade_db_to_v2
