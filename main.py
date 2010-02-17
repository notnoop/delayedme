#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Mahmood Ali on 2010-02-15.
Copyright (c) 2010 Jude LLC. All rights reserved.
"""

import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api import users
from models import Notification
import utils

class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            uri = users.create_login_url('/')
            self.redirect(uri)
            return

        template_values = {
            'notifications': Notification.all().filter('owner = ', user),
            'user': user
        }

        path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        self.response.out.write(template.render(path, template_values))

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
        
        message = notification.get_msg()
        message.subject = '[Reminder] ' + message.subject
        
        reminder_email = utils.format_reminder_email(message.)
        message.to = message.sender
        message.sender = utils.format_reminder_email(notification.delay_str)
        message.send()

        notification.sent = True
        notification.put()

application = webapp.WSGIApplication(
                                     [('/fire', TaskHandler),
                                      ('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
