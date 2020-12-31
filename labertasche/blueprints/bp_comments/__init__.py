#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /**********************************************************************************
#  * _author  : Domeniko Gentner
#  * _mail    : code@tuxstash.de
#  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
#  * _license : This project is under MIT License
#  *********************************************************************************/
import re
from sys import stderr
from antispam import is_spam as spam, score
from flask import Blueprint, jsonify, request, make_response, redirect
from flask_cors import cross_origin
from sqlalchemy import exc
from labertasche.database import labertasche_db as db
from labertasche.helper import is_valid_json, default_timestamp, check_gravatar, export_location
from labertasche.mail import Mail
from labertasche.models import TComments, TLocation, TEmail, TProjects
from labertasche.settings import Smileys
from secrets import compare_digest

# Blueprint
bp_comments = Blueprint("bp_comments", __name__, url_prefix='/comments')


# Route for adding new comments
@bp_comments.route("/<name>/new", methods=['POST'])
def check_and_insert_new_comment(name):

    # Get project
    project = db.session.query(TProjects).filter(TProjects.name == name).first()

    # Check refferer, this is not bullet proof
    if not compare_digest(request.origin, project.blogurl):
        return make_response(jsonify(status="not-allowed"), 403)

    if not project:
        return make_response(jsonify(status="post-project-not-found"), 400)

    if compare_digest(request.method, "POST"):
        smileys = Smileys()
        sender = Mail()

        # Check length of content and abort if too long or too short
        if request.content_length > 2048:
            return make_response(jsonify(status="post-max-length"), 400)
        if request.content_length == 0:
            return make_response(jsonify(status="post-min-length"), 400)

        # get json from request
        new_comment = request.json

        # save and sanitize location, nice try, bitch
        location = new_comment['location'].strip().replace('.', '')

        # Validate json and check length again
        if not is_valid_json(new_comment) or \
                len(new_comment['content']) < 40 or \
                len(new_comment['email']) < 5:
            print("too short", file=stderr)
            return make_response(jsonify(status='post-invalid-json'), 400)

        # Strip any HTML from message body
        tags = re.compile('<.*?>')
        special = re.compile('[&].*[;]')
        content = re.sub(tags, '', new_comment['content']).strip()
        content = re.sub(special, '', content).strip()

        # Convert smileys if enabled
        if project.addon_smileys:
            for key, value in smileys.smileys.items():
                content = content.replace(key, value)

        # Validate replied_to field is integer
        replied_to = new_comment['replied_to']
        try:
            if replied_to:
                replied_to = int(replied_to)

        # not a valid id at all
        except ValueError:
            return make_response(jsonify(status="bad-reply"), 400)

        # Update values
        new_comment.update({"content": content})
        new_comment.update({"email": new_comment['email'].strip()})
        new_comment.update({"location": location})
        new_comment.update({"replied_to": replied_to})

        # Check mail
        if not sender.validate(new_comment['email']):
            return make_response(jsonify(status='post-invalid-email'), 400)

        # check for spam
        is_spam = spam(new_comment['content'])
        has_score = score(new_comment['content'])

        # Insert mail into spam if detected, allow if listed as such
        email = db.session.query(TEmail).filter(TEmail.email == new_comment['email']).first()
        if not email:
            if is_spam:
                entry = {
                    "email": new_comment['email'],
                    "is_blocked": True,
                    "is_allowed": False
                }
                db.session.add(TEmail(**entry))
        if email:
            if not email.is_allowed:
                is_spam = True
            if email.is_allowed:
                # This forces the comment to be not spam if the address is in the allowed list,
                # but the commenter will still need to confirm it to avoid brute
                # force attacks against this feature
                is_spam = False

        # Look for location
        loc_query = db.session.query(TLocation) \
            .filter(TLocation.location == new_comment['location'])

        if loc_query.first():
            # Location exists, set existing location id
            new_comment.update({'location_id': loc_query.first().id_location})
            # TComments does not have this field
            new_comment.pop("location")
        else:
            # Insert new location
            loc_table = {
                'location': new_comment['location'],
                'project_id': project.id_project
            }
            new_loc = TLocation(**loc_table)
            db.session.add(new_loc)
            db.session.flush()
            db.session.refresh(new_loc)
            new_comment.update({'location_id': new_loc.id_location})

            # TComments does not have this field
            new_comment.pop("location")

        # insert comment
        # noinspection PyBroadException
        try:
            if project.sendotp:
                new_comment.update({"is_published": False})
            else:
                new_comment.update({"is_published": True})
            new_comment.update({"created_on": default_timestamp()})
            new_comment.update({"is_spam": is_spam})
            new_comment.update({"spam_score": has_score})
            new_comment.update({"gravatar": check_gravatar(new_comment['email'], project.name)})
            new_comment.update({"project_id": project.id_project})
            t_comment = TComments(**new_comment)
            db.session.add(t_comment)
            db.session.commit()
            db.session.flush()
            db.session.refresh(t_comment)

            # Send confirmation link and store returned value
            if project.sendotp:
                hashes = sender.send_confirmation_link(new_comment['email'], project.name)
                setattr(t_comment, "confirmation", hashes[0])
                setattr(t_comment, "deletion", hashes[1])
                db.session.commit()

        except exc.IntegrityError as e:
            # Comment body exists, because content is unique
            print(f"Duplicate from {request.environ['REMOTE_ADDR']}, error is:\n{e}", file=stderr)
            return make_response(jsonify(status="post-duplicate"), 400)

        except Exception:  # must be at bottom
            return make_response(jsonify(status="post-internal-server-error"), 400)

        export_location(t_comment.location_id)
        return make_response(jsonify(status="post-success",
                                     comment_id=t_comment.comments_id,
                                     sendotp=project.sendotp), 200)


# Route for confirming comments
@bp_comments.route("/<name>/confirm/<email_hash>", methods=['GET'])
@cross_origin()
def check_confirmation_link(name, email_hash):
    comment = db.session.query(TComments).filter(TComments.confirmation == email_hash).first()
    project = db.session.query(TProjects).filter(TProjects.name == name).first()

    if comment:
        location = db.session.query(TLocation).filter(TLocation.id_location == comment.location_id).first()
        if compare_digest(comment.confirmation, email_hash):
            comment.confirmation = None
            if not comment.is_spam:
                setattr(comment, "is_published", True)
            db.session.commit()
            url = f"{project.blogurl}{location.location}#comment_{comment.comments_id}"
            export_location(location.id_location)
            return redirect(url)

    return redirect(f"{project.blogurl}?cnf=true")


# Route for deleting comments
@bp_comments.route("<name>/delete/<email_hash>", methods=['GET'])
@cross_origin()
def check_deletion_link(name, email_hash):
    project = db.session.query(TProjects).filter(TProjects.name == name).first()
    comment = db.session.query(TComments).filter(TComments.deletion == email_hash).first()

    if comment:
        location = db.session.query(TLocation).filter(TLocation.id_location == comment.location_id).first()
        if compare_digest(comment.deletion, email_hash):
            print("True")
            db.session.delete(comment)
            db.session.commit()
            url = f"{project.blogurl}?deleted=true"
            export_location(location.id_location)
            return redirect(url)

    return redirect(f"{project.blogurl}?cnf=true")
