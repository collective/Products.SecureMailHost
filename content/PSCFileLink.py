"""
$Id: PSCFileLink.py,v 1.3 2005/03/09 18:04:43 dtremea Exp $
"""

import re

from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions

from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import registerType
from Products.Archetypes.public import DisplayList

from Products.PloneSoftwareCenter.config import PROJECTNAME
from Products.PloneSoftwareCenter.utils import std_modify_fti
from Products.PloneSoftwareCenter.content.schemata import PSCFileLinkSchema

def modify_fti(fti):
    std_modify_fti(fti)


class PSCFileLink(BaseContent):
    """Contains a link to a downloadable file for a Release."""

    __implements__ = (BaseContent.__implements__)

    archetype_name = 'Externally Hosted File'
    immediate_view = default_view = 'psc_file_view'
    content_icon = 'link_icon.gif'
    schema = PSCFileLinkSchema

    security = ClassSecurityInfo()

    actions = (
        {
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/psc_file_view',
            'permissions': (CMFCorePermissions.View,),
        },
    )

    security.declareProtected(CMFCorePermissions.View, 'getPlatformVocab')
    def getPlatformVocab(self):
        """Get the platforms available for selection via acquisition from
        the top-level package container.
        """
        return DisplayList([(item, item) for item in \
                            self.getAvailablePlatforms()])

    security.declareProtected(CMFCorePermissions.View, 'getDownloadIconName')
    def getDownloadIconName(self):
        """Given the currently selected platform, return the name of the
        name of the icon to use.

        This takes the form platform_${name}.gif, where ${name} is the
        platform name, in lowercase, with all non-alpha-numeric characters
        (including whitespace) converted to underscores.
        """
        return 'platform_%s.gif' % \
                    re.sub(r'\W', '_', self.getPlatform()).lower()

    security.declareProtected(CMFCorePermissions.View, 'getFileSize')
    def getFileSize(self):
        """Return the file size of the download, or None if unknown.
        """
        return None

    security.declareProtected(CMFCorePermissions.View, 'getDirectURL')
    def getDirectURL(self):
        """Get the direct URL to the download.
        """
        return self.getExternalURL()


registerType(PSCFileLink, PROJECTNAME)