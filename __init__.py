"""
PloneCollectorNG - A Plone-based bugtracking system

(C) 2002-2004, Andreas Jung

ZOPYX Software Development and Consulting Andreas Jung
Charlottenstr. 37/1
D-72070 T�bingen, Germany
Web: www.zopyx.com
Email: info@zopyx.com 

License: see LICENSE.txt

$Id: __init__.py,v 1.24 2004/11/12 15:37:52 ajung Exp $
"""

import os, sys

from Globals import package_home
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from config import SKINS_DIR, GLOBALS, PROJECTNAME
from config import ADD_CONTENT_PERMISSION

d = os.path.dirname(__file__)
if not d in sys.path:
    sys.path.append(d)

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):

    ##Import Types here to register them
    import Collector, Issue

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
    
    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)


    # Install workflow factories
    from Products.PloneCollectorNG.workflows import pcng_issue_workflow
    from Products.PloneCollectorNG.workflows import pcng_simple_workflow

from Products.PythonScripts.Utility import allow_module
allow_module('textwrap')
allow_module('group_assignment_policies')
allow_module('base64')

# Perform initialization of PCNG add-ons
try:
    import PCNGAddOn
except ImportError:
    pass
