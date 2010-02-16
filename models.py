#!/usr/bin/env python
# encoding: utf-8
"""
models.py

Created by Mahmood Ali on 2010-02-15.
Copyright (c) 2010 Jude LLC. All rights reserved.
"""

from google.appengine.ext import db

class Notification(db.Model):
    user = db.StringProperty()
    fire_time = db.DateTimeProperty()
    delay_str = db.StringProperty()

    email = db.TextProperty()

    sent = db.BooleanProperty(default=False)
