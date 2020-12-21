#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from platform import system
from labertasche.settings import LegacySettings
from os import access, W_OK
from sys import exit

print("""
This will convert the current config file to the new system. 
This will create new files in /etc/labertasche:
    - .secret: The current secret of this app
    - credentials.yaml: This file will contain your selected username and password
    - labertasche.yaml: This file will contain the basic configuration
    - smileys.yaml: This will contain all your smileys.    
""")

base_path = '.'
if system().lower() == 'linux':
    base_path = '/etc/labertasche/'


if not access(base_path, W_OK):
    print(f"I do not have write access to this path: {base_path}. Please correct that and run the script again.")
    exit(1)

# noinspection PyBroadException
try:
    legacy = LegacySettings()
    legacy.convert_to_v2()
except Exception as e:
    print("""
    Something went wrong. Your config is still available as labertasche.bak. 
    Consider reporting this as a bug on github please. The message was:\n
    """)
    print(str(e))
    exit(1)

print("""
    The upgrade is now complete. Your previous settings file has been stored as labertasche.bak.
    LEAVE THIS FILE AS IS UNTIL AFTER THE DATABASE UPGRADE! 
    Please start the flask app and follow the database upgrade instructions.
""")
