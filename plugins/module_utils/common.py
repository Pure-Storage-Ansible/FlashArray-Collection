# -*- coding: utf-8 -*-

# Copyright (c) 2024 Simon Dodsley, <simon@purestorage.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
This module adds shared functions for the FlashArray modules
"""


def human_to_bytes(size):
    """Given a human-readable byte string (e.g. 2G, 30M),
    return the number of bytes.  Will return 0 if the argument has
    unexpected form.
    """
    bytes = size[:-1]
    unit = size[-1].upper()
    if bytes.isdigit():
        bytes = int(bytes)
        if unit == "P":
            bytes *= 1125899906842624
        elif unit == "T":
            bytes *= 1099511627776
        elif unit == "G":
            bytes *= 1073741824
        elif unit == "M":
            bytes *= 1048576
        elif unit == "K":
            bytes *= 1024
        else:
            bytes = 0
    else:
        bytes = 0
    return bytes


def human_to_real(iops):
    """Given a human-readable string (e.g. 2K, 30M IOPs),
    return the real number.  Will return 0 if the argument has
    unexpected form.
    """
    digit = iops[:-1]
    unit = iops[-1].upper()
    if unit.isdigit():
        digit = iops
    elif digit.isdigit():
        digit = int(digit)
        if unit == "M":
            digit *= 1000000
        elif unit == "K":
            digit *= 1000
        else:
            digit = 0
    else:
        digit = 0
    return digit


def convert_to_millisecs(hour):
    """Convert a 12-hour clock to milliseconds from
    midnight"""
    if hour[-2:].upper() == "AM" and hour[:2] == "12":
        return 0
    elif hour[-2:].upper() == "AM":
        return int(hour[:-2]) * 3600000
    elif hour[-2:].upper() == "PM" and hour[:2] == "12":
        return 43200000
    return (int(hour[:-2]) + 12) * 3600000


def convert_time_to_millisecs(time):
    """Convert a time period in milliseconds"""
    if time[-1:].lower() not in ["w", "d", "h", "m", "s"]:
        return 0
    try:
        if time[-1:].lower() == "w":
            return int(time[:-1]) * 7 * 86400000
        elif time[-1:].lower() == "d":
            return int(time[:-1]) * 86400000
        elif time[-1:].lower() == "h":
            return int(time[:-1]) * 3600000
        elif time[-1:].lower() == "m":
            return int(time[:-1]) * 60000
    except Exception:
        return 0
