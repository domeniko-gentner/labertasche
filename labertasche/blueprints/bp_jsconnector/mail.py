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
from flask_cors import cross_origin
from labertasche.database import labertasche_db as db
from labertasche.models import TEmail


@cross_origin()
@bp_jsconnector.route('/mail-toggle-status/<int:id_email>')
@login_required
def api_toggle_email_reputation(id_email):
    address = db.session.query(TEmail).filter(TEmail.id_email == id_email).first()
    if address:
        setattr(address, "is_allowed", (not address.is_allowed))
        setattr(address, "is_blocked", (not address.is_blocked))
        db.session.commit()
    return redirect(request.referrer)


@cross_origin()
@bp_jsconnector.route('/mail-reset-reputation/<int:id_email>')
@login_required
def api_reset_mail_reputation(id_email):
    db.session.query(TEmail).filter(TEmail.id_email == id_email).delete()
    db.session.commit()
    return redirect(request.referrer)


