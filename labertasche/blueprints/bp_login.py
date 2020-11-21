#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from flask import Blueprint, render_template, request, redirect, url_for
from flask_cors import cross_origin
from labertasche.helper import check_auth, User
from flask_login import login_user, current_user, logout_user

# Blueprint
bp_login = Blueprint("bp_login", __name__)


@cross_origin()
@bp_login.route('/', methods=['GET'])
def show_login():
    if current_user.is_authenticated:
        return redirect(url_for('bp_dashboard.dashboard_index'))
    return render_template('login.html')


@cross_origin()
@bp_login.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if check_auth(username, password):
            login_user(User(0), remember=True)
            return redirect(url_for('bp_dashboard.dashboard_index'))

    # Redirect get request to the login page
    return redirect(url_for('bp_login.show_login'))


@cross_origin()
@bp_login.route('/logout/', methods=["GET"])
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("bp_login.show_login"))
