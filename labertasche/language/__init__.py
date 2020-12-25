#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from flask import Request
from pathlib import Path
from json import load


class Language:

    def __init__(self, request: Request):
        # Define data
        self.i18n = dict()
        self.languages = list()

        # Directory where translations live
        i18n_dir = Path('./i18n').absolute()

        # Looks for translations
        for filename in i18n_dir.glob("*.json"):
            if filename.is_file():
                self.languages.append(filename.stem)

        # Check the browser language in the headers
        self.browser_language = request.accept_languages.best_match(self.languages, default="en-US")

        # Try to Load language accepted by browser
        try:
            file = i18n_dir / self.browser_language
            with file.with_suffix(".json").absolute().open('r', encoding='utf-8') as fp:
                foreign = load(fp)
        except FileNotFoundError:
            pass

        # Always load english
        file = i18n_dir / "en-US"
        with file.with_suffix(".json").absolute().open('r', encoding='utf-8') as fp:
            self.i18n = load(fp)

        # Merge dicts, so missing keys are replaced with English
        self.i18n.update(**foreign)

