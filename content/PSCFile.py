"""
$Id: PSCFile.py,v 1.2 2005/03/05 02:04:25 optilude Exp $
"""

from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import registerType
from Products.Archetypes.public import DisplayList

from Products.PloneSoftwareCenter.utils import std_modify_fti
from Products.PloneSoftwareCenter.config import PROJECTNAME

from Products.CMFCore import CMFCorePermissions

from AccessControl import ClassSecurityInfo

from schemata import PSCFileSchema

import re

def modify_fti(fti):
    std_modify_fti(fti)

class PSCFile(BaseContent):
    """Contains the downloadable file for the Release."""

    security = ClassSecurityInfo()
    __implements__ = (BaseContent.__implements__)

    archetype_name = 'Software File'
    immediate_view = default_view = 'download_view'
    content_icon = 'file_icon.gif'
    schema = PSCFileSchema
    
    actions = ({
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${object_url}/psc_download_view',
        'permissions' : (CMFCorePermissions.View,)
         },
         )


    def getPlatformVocab(self):
        """Get the platforms available for selection via acquisition from
        the top-level package container.
        """
        return DisplayList ([(item, item) for item in \
                                self.getAvailablePlatforms ()])
                
    security.declareProtected(CMFCorePermissions.View, 'getDownloadIconName')                
    def getDownloadIconName(self):
        """Given the currently selected platform, return the name of the
        name of the icon to use. This takes the form platform_${name}.gif,
        where ${name} is the platform name, in lowercase, with all non-alpha-
        numeric characters (including whitespace) converted to underscores.
        """
        return "platform_%s.gif" % \
                    (re.sub(r'\W', '_', self.getPlatform()).lower(),)

registerType(PSCFile, PROJECTNAME)
