#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from json import load as j_load
from pathlib import Path
from platform import system
from smtplib import SMTP_SSL, SMTPHeloError, SMTPAuthenticationError, SMTPException
from ssl import create_default_context
from validate_email import validate_email_or_fail
from secrets import token_urlsafe
from labertasche.models import TProjects
from labertasche.database import labertasche_db as db
from labertasche.settings import Settings
from labertasche.language import Language
from flask import render_template, request


class Mail:

    def __init__(self):
        path = Path("/etc/labertasche/mail_credentials.json")
        if system().lower() == "windows":
            path = Path("mail_credentials.json")

        with path.open("r") as fp:
            self.credentials = j_load(fp)

    def send(self, txt_what: str, html_what: str, to: str):
        if not self.credentials['enable']:
            return

        txtmail = MIMEText(txt_what, "plain", _charset='utf8')

        multimime = MIMEMultipart('alternative')
        multimime['Subject'] = "Comment confirmation pending"
        multimime['From'] = self.credentials['email-sendfrom']
        multimime['To'] = to
        multimime.attach(txtmail)

        # Only send HTML if needed
        if html_what is not None:
            htmlmail = MIMEText(html_what, "html",  _charset='utf8')
            multimime.attach(htmlmail)

        try:
            with SMTP_SSL(host=self.credentials['smtp-server'],
                          port=self.credentials['smtp-port'],
                          context=create_default_context()) as server:
                server.login(user=self.credentials['email-user'], password=self.credentials['email-password'])
                server.sendmail(to_addrs=to,
                                msg=multimime.as_string(),
                                from_addr=self.credentials['email-sendfrom'])

        except SMTPHeloError as helo:
            print(f"SMTPHeloError: {helo}")
        except SMTPAuthenticationError as auth_error:
            print(f"Authentication Error: {auth_error}")
        except SMTPException as e:
            print(f"SMTPException: {e}")

    def send_confirmation_link(self, email: str, name: str) -> tuple:
        """
        Send confirmation link after entering a comment
        :param email: The address to send the mail to
        :param name: The name of the project
        :return: A tuple with the confirmation token and the deletion token, in this order
        """
        project = db.session.query(TProjects).filter(TProjects.name == name).first()
        if not project:
            return None, None

        settings = Settings()
        language = Language(request)

        confirm_digest = token_urlsafe(48)
        delete_digest = token_urlsafe(48)

        confirm_url = f"{settings.weburl}/comments/{project.name}/confirm/{confirm_digest}"
        delete_url = f"{settings.weburl}/comments/{project.name}/delete/{delete_digest}"

        html_tpl = f"mail/comment_confirmation_{language.browser_language}.html"
        txt_tpl = f"mail/comment_confirmation_{language.browser_language}_txt.html"

        if not Path(f"./templates/{html_tpl}").exists():
            html_tpl = f"mail/comment_confirmation_en-US.html"
        if not Path(f"./templates/{txt_tpl}").exists():
            html_tpl = f"mail/comment_confirmation_en-US_txt.html"

        txt_what = render_template(txt_tpl,
                                   blogurl=project.blogurl,
                                   confirmation_url=confirm_url,
                                   deletion_url=delete_url).replace('<pre>', "").replace('</pre>', '')

        html_what = render_template(html_tpl,
                                    blogurl=project.blogurl,
                                    confirmation_url=confirm_url,
                                    deletion_url=delete_url)

        self.send(txt_what, html_what, email)
        return confirm_digest, delete_digest

    def validate(self, addr):
        # validate email
        is_valid = validate_email_or_fail(email_address=addr, check_regex=True, check_mx=False,
                                          dns_timeout=10, use_blacklist=True, debug=False)
        return is_valid
