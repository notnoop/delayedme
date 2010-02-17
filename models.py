#!/usr/bin/env python
# encoding: utf-8
"""
models.py

Created by Mahmood Ali on 2010-02-15.
Copyright (c) 2010 Jude LLC. All rights reserved.
"""
import pickle

from google.appengine.ext import db

class Notification(db.Model):
    """
    A 
    """
    sender = db.StringProperty()
    owner = db.UserProperty()

    fire_time = db.DateTimeProperty()
    delay_str = db.StringProperty()

    email = db.TextProperty()
    subject = db.TextProperty()

    sent = db.BooleanProperty(default=False)

    def set_msg(self, msg):
        self.email = pickle.dumps(msg)

    def get_msg(self):
        return pickle.loads(str(self.email))

    def __str__(self):
        return 'Notification %s - %s' % (self.sender, self.subject, )
