#!/usr/bin/env python
# encoding: utf-8
"""
handle_email.py

Created by Mahmood Ali on 2010-02-15.
Copyright (c) 2010 Jude LLC. All rights reserved.
"""

import pickle
import logging, datetime
import utils

from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users

from models import Notification
import tasks

def schedule_notification(notification):
	fire_time = notification.fire_time
	id = notification.key().id()
	taskqueue.add(url='/fire', params={'id':id },
				  eta=fire_time)

class NotificationEmailHandler(InboundMailHandler):
    def receive(self, msg):
        notification = Notification()
        notification.sender = msg.sender
        delay = utils.target_username(msg.to)
        notification.owner = users.User(utils.address_part(msg.sender))

        notification.delay_str = delay
        notification.fire_time = datetime.datetime.now() + utils.parse_timedelta(delay)
        
        notification.email = pickle.dumps(msg)
        notification.subject = msg.subject

        notification.put()
        schedule_notification(notification)
        logging.info("Received a message from: " + msg.sender)

application = webapp.WSGIApplication([NotificationEmailHandler.mapping()], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
