#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Mahmood Ali on 2010-02-15.
Copyright (c) 2010 Jude LLC. All rights reserved.
"""

import pickle
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models import Notification
import utils

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')

class TaskHandler(webapp.RequestHandler):
    def get(self):
        self.redirect('/')

    def post(self):
        id = long(self.request.get('id'))
        notification = Notification.get_by_id(id)
        logging.warning('Notif %s' % notification)

        if (notification == None):
            self.response.out.write('Notification not found: %d\n\r' % id)
            return
        
        message = pickle.loads(str(notification.email))
        message.subject = '[Reminder] ' + message.subject
        
        reminder_email = utils.format_reminder_email(message.to)
        message.to = message.sender
        message.sender = reminder_email
        message.send()

        notification.sent = True

application = webapp.WSGIApplication(
                                     [('/fire', TaskHandler),
                                      ('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
