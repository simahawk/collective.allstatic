#-*- coding: utf-8 -*-

# ===============================================
# Script for exporting static resources
# ===============================================

import os
import sys
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Testing.makerequest import makerequest
from Products.CMFCore.tests.base.security import (PermissiveSecurityPolicy,
                                                  OmnipotentUser)

from zope.component.hooks import setSite


def spoofRequest(app):
    """
    Make REQUEST variable to be available on the Zope application server.

    This allows acquisition to work properly
    """
    _policy = PermissiveSecurityPolicy()
    setSecurityPolicy(_policy)
    newSecurityManager(None, OmnipotentUser().__of__(app.acl_users))
    return makerequest(app)

# Enable Faux HTTP request object
app = spoofRequest(app)

try:
    site_id = sys.argv[3]
except:
    site_id = 'Plone'

site = getattr(app, site_id)
setSite(site)

try:
    what = sys.argv[4].lower()
except:
    what = 'css'

if not what in ('css', 'js'):
    print "2nd arg must be js or css"
    sys.exit(0)

_extra_args = sys.argv[5:]
conf = {}

for i, k in enumerate(_extra_args):
    if k in ('-wl', '-bl', '-fn'):
        conf[k[1:]] = _extra_args[i + 1]


def get_content(site, what, wl=None, bl=None):
    view = site.restrictedTraverse('all.' + what)
    return view(whitelist=wl, blacklist=bl)


def get_lists(**kw):
    vals = {}
    for k in ('bl', 'wl'):
        fname = kw.get(k)
        if fname is None:
            continue
        if not os.path.exists(fname):
            print "Provided file `", k, "` does not exists!"
            sys.exit(0)
        with open(fname, 'r') as fd:
            ct = fd.read()
            vals[k] = [x.strip()
                       for x in ct.splitlines()]
            print 'Using list `', k, '`, Will skip:'
            print ct.strip()
    return vals.get('bl'), vals.get('wl')


def run():
    bl, wl = get_lists(**conf)
    content = get_content(site, what, wl=wl, bl=bl)
    if isinstance(content, unicode):
        content = content.encode('utf-8')
    fl = conf.get('fn', 'exported.' + what)
    with open(fl, 'w') as output:
        output.write(content)
    print '############################################'
    print 'Exported', what.upper(), 'to', fl
    print '############################################'

run()
