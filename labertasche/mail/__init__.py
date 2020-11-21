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
from labertasche.settings import Settings
from validate_email import validate_email
from secrets import token_urlsafe


class mail:

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

    def send_confirmation_link(self, email):
        """
        Send confirmation link after entering a comment
        :param email: The address to send the mail to
        :return: A tuple with the confirmation token and the deletion token, in this order
        """
        settings = Settings()
        confirm_digest = token_urlsafe(48)
        delete_digest = token_urlsafe(48)

        confirm_url = f"{settings.system['web_url']}/comments/confirm/{confirm_digest}"
        delete_url = f"{settings.system['web_url']}/comments/delete/{delete_digest}"

        txt_what = f"Hey there. You have made a comment on {settings.system['blog_url']}. Please confirm it by " \
                   f"copying this link into your browser:\n{confirm_url}\nIf you want to delete your comment for,"\
                   f"whatever reason, please use this link:\n{delete_url}"

        html_what = f"Hey there. You have made a comment on {settings.system['blog_url']}.<br>Please confirm it by " \
                    f"clicking on this <a href='{confirm_url}'>link</a>.<br>"\
                    f"In case you want to delete your comment later, please click <a href='{delete_url}'>here</a>."\
                    f"<br><br>If you think this is in error or someone made this comment in your name, please "\
                    f"write me a <a href='mailto:contact@tuxstash.de'>mail</a> to discuss options such as " \
                    f"blocking your mail from being used."

        self.send(txt_what, html_what, email)

        return confirm_digest, delete_digest

    def validate(self, addr):
        # validate email
        is_valid = validate_email(email_address=addr,
                                  check_regex=True,
                                  check_mx=False,
                                  dns_timeout=10,
                                  use_blacklist=True,
                                  debug=False)
        return is_valid
