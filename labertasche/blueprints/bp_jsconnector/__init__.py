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
bp_jsconnector = Blueprint("bp_jsconnector", __name__, url_prefix='/api/')

from .projects import api_create_project, api_delete_project, api_edit_project_name
from .mail import api_toggle_email_reputation, api_reset_mail_reputation
from .comments import api_comment_allow_user, api_comment_allow_comment, \
                      api_comment_block_mail, api_comments_delete_comment
