from AccessControl import ModuleSecurityInfo
from Globals import package_home
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils as CMFCoreUtils
from Products.CMFCore.DirectoryView import registerDirectory
import os, os.path

# Get all the content types in the types directory
from Products.PloneHelpCenter.types import * 

from config import SKINS_DIR, GLOBALS, PROJECTNAME
from config import ADD_CONTENT_PERMISSION

registerDirectory(SKINS_DIR, GLOBALS)

# MonkeyPatch CMFDefault.DiscussionItemContainer
import Patch

# make comment_notify importable ttw
from utils import discussion_notify
ModuleSecurityInfo('Products.PloneHelpCenter').declarePublic('discussion_notify')

def initialize(context):

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
 
    CMFCoreUtils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

    # Force the loading of test data generation scripts that
    # we're currently attaching to the portal_migration tool.
    # XXX: Remove this hack when we final have a portal_test_script tool.
    import tests
