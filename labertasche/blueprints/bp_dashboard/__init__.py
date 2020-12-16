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
bp_dashboard = Blueprint("bp_dashboard", __name__, url_prefix='/dashboard')

# Files with routes
from .projects import dashboard_project_list
from .mail import dashboard_manage_mail
from .spam import dashboard_review_spam
from .comments import dashboard_manage_regular_comments
