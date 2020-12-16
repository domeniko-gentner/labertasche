#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
import yaml
from pathlib import Path
from platform import system


class Settings:
    """
        Automatically loads the settings from /etc/ on Linux and same directory on other OS
    """
    def __init__(self):
        file = Path("labertasche.yaml")
        if system().lower() == "linux":
            file = Path("/etc/labertasche/labertasche.yaml")

        with file.open('r') as fp:
            conf = yaml.safe_load(fp)

        self.system = conf['system']
        self.dashboard = conf['dashboard']
        self.gravatar = conf['gravatar']
        self.addons = conf['addons']
        self.smileys = conf['smileys']
        self.projects = conf['projects']
