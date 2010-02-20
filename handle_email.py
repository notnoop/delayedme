#!/usr/bin/env python
# encoding: utf-8
"""
handle_email.py

Created by Mahmood Ali on 2010-02-15.
Copyright (c) 2010 Jude LLC. All rights reserved.
"""

import logging, datetime
import utils

from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.api import mail

from models import Notification

SENDER = 'DelayedMe Reminder <admin@delayedme.appspotmail.com>'

def schedule_notification(notification):
    """
    Schedule a task to send the notification at its fire time

    """
    fire_time = notification.fire_time
    id = notification.key().id()
    name = 'reminder-' + str(id)
    taskqueue.add(url='/fire', params={'id':id },
                  eta=fire_time, name=name)

def strip_attachments(msg):
    if hasattr(msg, 'attachments') and msg.attachments:
        del msg.attachments
        for part in msg.original.walk():
            if (part.get('Content-Disposition')
                and part.get('Content-Disposition').startswith("attachment")):

                part.set_type("text/plain")
                part.set_payload("Attachment removed: %s (%s, %d bytes)"
                                %(part.get_filename(), 
                                part.get_content_type(), 
                                len(part.get_payload(decode=True))))
                del part["Content-Disposition"]
                del part["Content-Transfer-Encoding"]

def strip_cc(msg):
    if hasattr(msg, 'cc') and msg.cc:
        del msg.cc
        del msg.original['cc']

class NotificationEmailHandler(InboundMailHandler):
    """
    And email handler that persist the email message in order to
    resend it later.  The handler uses the username of the target email
    (e.g. '3sec' in '3sec@domain.com') to determine the delay
    
    """

    def handle_error(self, msg, e):
        logging.error(
                'Cannot schedule delayed message %s - %s as found error\n %s'
                % (msg.sender, msg.subject, str(e),))
        mail.send_mail(sender=SENDER,
                    to=msg.sender,
                    subject='[ERROR] Re: ' + msg.subject,
                    body="""
Dear user,

Sorry but we couldn't schedule the following message:

From: %s
Subject: %s

Error message description:
    %s

                    """ % (msg.sender, msg.subject, str(e),))

    def receive(self, msg):
        try:
            self.persist_message(msg)
        except Exception, e:
            self.handle_error(msg, e)
        except ValueError, e:
            self.handle_error(msg, e)

    def persist_message(self, msg):
        notification = Notification()
        notification.sender = msg.sender
        notification.owner = users.User(utils.address_part(msg.sender))

        # TODO: Handle invalid delays
        delay = utils.email_in_path(self.request.path)
        notification.delay_str = delay
        notification.fire_time = datetime.datetime.now() + utils.parse_timedelta(delay)

        strip_cc(msg)
        try:
            strip_attachments(msg)
        except Exception, e:
            logging.warning('Found warning ' + str(e))
            pass

        notification.set_msg(msg)
        notification.subject = msg.subject

        notification.put()
        schedule_notification(notification)
        logging.info("Received a message from: " + msg.sender)

application = webapp.WSGIApplication([NotificationEmailHandler.mapping()], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
