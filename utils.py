#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Mahmood Ali on 2010-02-15.
Copyright (c) 2010 Jude LLC. All rights reserved.
"""

import datetime
import re
import logging

UNIT_CLASSES = (
    ('seconds', 'second', 'sec', 'secs', 's',),
    ('minutes', 'minute', 'min', 'mins', 'm',),
    ('hours', 'hour', 'h',),
    ('days', 'day', 'd',),
    ('weeks', 'week', 'w',),
)

def to_dict(list):
    result = {}
    for row in list:
        result.update(dict([[v, row[0]] for v in row]))

    return result

UNIT_CANON = to_dict(UNIT_CLASSES)

times = re.compile(r"(\d+)[-_]?(\D+)").findall
def parse_timedelta(s):
    parsed = times(s)
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

def format_reminder_email(address):
    loc = address.find('<')
    if loc == -1:
        return 'Syphir Reminder <' + address + '>'
    else:
        return address

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
    import rfc822
    logging.warning('To     : %s' % email)
    to = rfc822.parseaddr(email)
    if (to[1] == None):
        return None

    return username_part(to[1])
