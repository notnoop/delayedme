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

from models import Notification

def schedule_notification(notification):
    """
    Schedule a task to send the notification at its fire time

    """
    fire_time = notification.fire_time
    id = notification.key().id()
    name = 'reminder-' + str(id)
    taskqueue.add(url='/fire', params={'id':id },
                  eta=fire_time, name=name)

class NotificationEmailHandler(InboundMailHandler):
    """
    And email handler that persist the email message in order to
    resend it later.  The handler uses the username of the target email
    (e.g. '3sec' in '3sec@domain.com') to determine the delay
    
    """

    def receive(self, msg):
        notification = Notification()
        notification.sender = msg.sender
        notification.owner = users.User(utils.address_part(msg.sender))

        # TODO: Handle invalid delays
        delay = utils.email_in_path(self.request.path)
        notification.delay_str = delay
        notification.fire_time = datetime.datetime.now() + utils.parse_timedelta(delay)

        if msg.cc:
            del msg.cc

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
