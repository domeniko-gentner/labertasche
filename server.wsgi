#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from sys import path as sys_path
from os import path as os_path

sys_path.insert(0, os_path.dirname(os_path.realpath(__file__)))

from server import laberflask
application = laberflask
