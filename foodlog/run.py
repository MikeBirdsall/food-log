#!/usr/bin/env python3
""" Wrapper for the foodlog system

    This wrapper allows the foodlog cgi-bin programs to be run either by a
    user who is logged in (with BASIC-AUTH) or one who is not. Those programs
    can authorize appropriate operations (viewing and/or editing) the dieters
    data. This is used particularly to allow a dietitian to view the data, but
    not changes it.
    
    A copy (or a link to a copy) is placed in one directory which is protected
    and one that is not.

    The wrapper will call the actual top level of the program, which can use
    os.environ.get('REMOTE_USER') to determine if someone is logged on, and if
    so, whom.

    This wrapper is kept intentionally tiny; all the work that can be is kept
    in the included program
"""

from foodlog import Dispatch

Dispatch()
