#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from . import bp_jsconnector
from flask import make_response, jsonify, request
from flask_cors import cross_origin
from flask_login import login_required
from labertasche.language import Language


@cross_origin
@bp_jsconnector.route('/language/')
@login_required
def api_translation():
    lang = Language(request=request)
    return make_response(jsonify(lang.i18n), 200)
