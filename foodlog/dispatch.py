""" Command Dispatch for the foodlog system

   The foodlog system is intended to run as cgi-bin program.
   The URL should be of the form:

        https://...?cmd=<cmd>;par1=par1;par2=par2

    where the parN parameters depend on the command, and this dispatcher
    directs to the appropriate code for each value of cmd, and whether the user
    is logged in or not.

"""

import cgi
import cgitb; cgitb.enable() # pylint: disable=C0321
import os

VIEW_VALID = set('report detail'.split())
EDIT_VALID = VIEW_VALID.union("""enter copy delete edit search
    template""".split())

def Dispatch():
    """ Finds the user and command and passes control on """

    user = os.environ.get('REMOTE_USER')
    form = cgi.FieldStorage()

    if "cmd" not in form:
        print(TEMPLATE_A)
        cgi.print_form(form)
        query = os.environ.get('QUERY_STRING') or "Empty Query String"
        print(NO_CMD_ERROR.format(query))
        return

    cmd = set(form.getlist("cmd"))
    if len(cmd) != 1:
        print(MULTIPLE_CMDS_ERROR.format(cmd))
        return

    cmd = cmd.pop()

    if not user and cmd not in VIEW_VALID:
        print(INVALID_CMD_ERROR.format(cmd, user, VIEW_VALID))
        return
    elif cmd not in EDIT_VALID:
        print(INVALID_CMD_ERROR.format(cmd, user, EDIT_VALID))
        return

    if cmd == 'report':
        from foodlog.report import Report
        Report(form, user)
    elif cmd == 'enter':
        from foodlog.form import EntryForm
        EntryForm(form, user).process()
    elif cmd == 'edit':
        from foodlog.edit import Edit
        Edit(form, user)
    elif cmd == 'detail':
        from foodlog.detail import ViewCourse
        ViewCourse(form, user)
    elif cmd == 'search':
        from foodlog.full_search import FullTextSearch
        FullTextSearch(form, user)
    elif cmd == 'template':
        from foodlog.copy_template import CopyTemplate
        CopyTemplate(form, user)
    else:
        print(NOT_IMPLEMENTED.format(cmd))



TEMPLATE_A = """content-type: text/html

<!DOCTYPE html>
<html lang="en">
  <head>
  <title>Text Basic Auth</title>
  </head>
  <body>

"""
TEMPLATE_B = """\

  </body>
</html>
"""

NO_CMD_ERROR = "No command in {}" + TEMPLATE_B
MULTIPLE_CMDS_ERROR = TEMPLATE_A + "Multiple commands in {}" + TEMPLATE_B
INVALID_CMD_ERROR = (TEMPLATE_A +
    "Invalid command {} for user {}. Valid commands are:{}" + TEMPLATE_B)
NOT_IMPLEMENTED = TEMPLATE_A + """
    Unimplemented command {}
"""

