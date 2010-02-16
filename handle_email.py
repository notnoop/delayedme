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

from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app

from models import Notification
import tasks

class LogSenderHandler(InboundMailHandler):
    def receive(self, msg):
        notification = Notification()
        notification.user = msg.sender
        delay = utils.target_username(msg.to)
        notification.delay_str = delay
        notification.fire_time = datetime.datetime.now() + utils.parse_timedelta(delay)
        
        notification.email = pickle.dumps(msg)
        notification.put()
        tasks.schedule_notification(notification)
        logging.info("Received a message from: " + msg.sender)

application = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
