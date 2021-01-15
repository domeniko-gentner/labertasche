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
from shutil import copy
from hashlib import pbkdf2_hmac
from secrets import compare_digest


def hash_password(password, secret=None):
    """
    Hashes the administrator password
    :param password: The password to hash
    :param secret: The site secret
    :return: The hashed value as a hexadecimal string
    """
    if not secret:
        secret = Secret()
    h = pbkdf2_hmac('sha512',
                    password=password.encode('utf8'),
                    salt=secret.key.encode('utf8'),
                    iterations=250000)
    return h.hex()


class Settings:

    def __init__(self):
        file = Path("labertasche.yaml")
        if system().lower() == "linux":
            file = Path("/etc/labertasche/labertasche.yaml")

        with file.open('r') as fp:
            conf = yaml.safe_load(fp)

        self.weburl = conf['system']['weburl']
        self.cookie_domain = conf['system']['cookie_domain']
        self.database_uri = conf['system']['database_uri']
        self.debug = conf['system']['debug']
        self.cookie_secure = conf['system']['cookie_secure']


class Secret:

    def __init__(self):
        file = Path(".secret")
        if system().lower() == "linux":
            file = Path("/etc/labertasche/.secret")

        with file.open('r') as fp:
            self.key = fp.readline()


class Smileys:

    def __init__(self):
        file = Path("smileys.yaml")
        if system().lower() == "linux":
            file = Path("/etc/labertasche/smileys.yaml")

        with file.open('r') as fp:
            conf = yaml.safe_load(fp)

        self.smileys = conf['smileys']


class Credentials:
    def __init__(self):
        file = Path("credentials.yaml")
        if system().lower() == "linux":
            file = Path("/etc/labertasche/credentials.yaml")

        with file.open('r') as fp:
            conf = yaml.safe_load(fp)

        self.username = conf['credentials']['username']
        self.password = conf['credentials']['password']

    def compare_password(self, userinput):
        """
        Compares 2 passwords with one another

        :param userinput: The input on the login page
        :return: True if the passwords match, otherwise False
        """
        secret = Secret()
        hashed = pbkdf2_hmac('sha512',
                             password=userinput.encode('utf8'),
                             salt=secret.key.encode('utf8'),
                             iterations=250000)
        return compare_digest(self.password, hashed.hex())


# deprecated, leave as is
class LegacySettings:
    """
        Automatically loads the settings from /etc/ on Linux and same directory on other OS
    """
    def __init__(self, use_backup: bool = False):
        file = Path("labertasche.yaml")
        if system().lower() == "linux":
            file = Path("/etc/labertasche/labertasche.yaml")

        # Use backup when conversion is done, this is used in db_v2.py
        if use_backup:
            file = file.with_suffix('.bak')

        with file.open('r') as fp:
            conf = yaml.safe_load(fp)

        self.system = conf['system']
        self.smileys = conf['smileys']
        self.dashboard = conf['dashboard']
        self.gravatar = conf['gravatar']
        self.addons = conf['addons']

    def convert_to_v2(self):
        old = Path("labertasche.yaml")
        if system().lower() == "linux":
            old = Path("/etc/labertasche/labertasche.yaml")

        systemvars = {
            'system': {
                'weburl': self.system['web_url'],
                'cookie_domain': self.system['cookie-domain'],
                'database_uri': self.system['database_uri'],
                'debug': self.system['debug'],
                'cookie_secure': False
            }
        }

        credentials = {
            'credentials': {
                'username': self.dashboard['username'],
                'password': hash_password(self.dashboard['password'], self.system['secret'])
            }
        }

        smileys = {
            'smileys': self.smileys
        }

        # backup old config
        copy(old, old.with_suffix('.bak'))

        # Write new config files
        p_sys = Path('labertasche.yaml')
        p_credentials = Path('credentials.yaml')
        p_smileys = Path('smileys.yaml')
        p_secret = Path('.secret')

        if system().lower() == 'linux':
            p_sys = '/etc/labertasche/' / p_sys
            p_credentials = '/etc/labertasche/' / p_credentials
            p_smileys = '/etc/labertasche/' / p_smileys
            p_secret = '/etc/labertasche/' / p_secret

        with p_sys.open('w') as fp:
            yaml.dump(systemvars, fp)
        with p_credentials.open('w') as fp:
            yaml.dump(credentials, fp)
        with p_smileys.open('w') as fp:
            yaml.dump(smileys, fp)
        with p_secret.open('w') as fp:
            fp.write(self.system['secret'])
