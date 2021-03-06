#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Mahmood Ali on 2010-02-15.
Copyright (c) 2010 Jude LLC. All rights reserved.
"""

import rfc822
import datetime
import re
import logging
import urllib

UNIT_CLASSES = (
    ('seconds', 'second', 'sec', 'secs', 's',),
    ('minutes', 'minute', 'min', 'mins', 'm',),
    ('hours', 'hour', 'h',),
    ('days', 'day', 'd',),
    ('weeks', 'week', 'w',),
)

MAIL_DOMAIN = 'delayedme.appspotmail.com'

def to_dict(list):
    result = {}
    for row in list:
        result.update(dict([[v, row[0]] for v in row]))

    return result

UNIT_CANON = to_dict(UNIT_CLASSES)

times = re.compile(r"(\d+)[-_]?(\D+)").findall
def parse_timedelta(s):
    parsed = times(s)
    if not parsed:
        raise ValueError('Could not parse time in ' + s)
    units = dict([[UNIT_CANON[v], int(k)] for k, v in parsed])
    return datetime.timedelta(**units)

def username_part(address):
    """
    Returns the username part of the email address

    >>> username_part('admin')
    'admin'

    >>> username_part('admin@what.com')
    'admin'

    """
    loc = address.find('@')
    if loc == -1:
        return address
    else:
        return address[0:loc]

def format_reminder_email(delay_period):
    return 'Syphir Reminder <' + delay_period + '@' + MAIL_DOMAIN + '>'

def target_username(email):
    """
    Returns the username part of the address

    >>> target_username('test@example.com')
    'test'

    >>> target_username('Tester <test@example.com>')
    'test'

    >>> target_username('"Test1" <test1@example.com>, mark@example.com')
    'test1'

    """
    logging.warning('To     : %s' % email)
    to = rfc822.parseaddr(email)
    if (to[1] == None):
        return None

    return username_part(to[1])

def address_part(email):
    """
    Returns the email part of the address
    
    >>> address_part('test@example.com')
    'test@example.com'
    
    >>> address_part('Tester <test@example.com>')
    'test@example.com'

    """
    return rfc822.parseaddr(email)[1]

def email_in_path(url):
    """
    Returns the target username in request path in GAE
    
    >>> email_in_path('/_ah/mail/30seconds@whatever.com')
    '30seconds'

    >>> email_in_path('/_ah/mail/30m%40what.com')
    '30m'

    """
    path = urllib.url2pathname(url)
    parts = path.split('/')
    return target_username(parts[3])
