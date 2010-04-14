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

def add_references(message):
    msg_id = message['Message-ID']
    del message['In-Reply-To']
    message['In-Reply-To'] = msg_id

    old_references = message['References']
    del message['References']
    if old_references:
        references = msg_id + '\r\n        ' + old_references
    else:
        references = msg_id
    message['References'] = references

class TaskHandler(webapp.RequestHandler):
    def get(self):
        self.redirect('/')

    def post(self):
        id = long(self.request.get('id'))
        notification = Notification.get_by_id(id)
        logging.debug('Notifying %s' % notification)

        if (notification == None):
            logging.warning('Couldnot find notification')
            self.response.out.write('Notification not found: %d\n\r' % id)
            return

        message = notification.get_msg()
        message.subject = message.subject

        message.to = message.sender
        message.sender = utils.format_reminder_email(notification.delay_str)

        try:
            add_references(message.original)
        except Exception, e:
            logging.warning(e)

        logging.info('sending email from %s' % message.sender)
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
