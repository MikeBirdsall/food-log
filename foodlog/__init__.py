# -*- coding: utf-8 -*-
"""
    foodlog
    ~~~~~~~

    Foodlog is a web program to track food intake with a philosophy of
    allowing minimal information to be added in initially, and filling in
    more later. IN particular, a picture of a meal can be put in (or just
    captured) including EXIF information about when (and where) the picture
    was taken, and then using that as a reminder to add nutrition and serving
    information later, either from the mobile device or from a laptop or
    desktop.
"""

__version__ = '0.1'


from foodlog.dispatch import Dispatch
