#!/usr/bin/env python
# encoding: utf-8
"""
tasks.py

Created by Mahmood Ali on 2010-02-15.
Copyright (c) 2010 Jude LLC. All rights reserved.
"""

from google.appengine.api.labs import taskqueue

def schedule_notification(notification):
	fire_time = notification.fire_time
	id = notification.key().id()
	taskqueue.add(url='/fire', params={'id':id },
				  eta=fire_time)
