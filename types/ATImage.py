#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2004 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA 
#
"""

$Id: ATImage.py,v 1.8 2004/05/14 12:36:04 godchap Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from urllib import quote

from Products.Archetypes.public import *
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    pass
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from Acquisition import aq_parent

from Products.ATContentTypes.config import *
from Products.ATContentTypes.types.ATContentType import ATCTContent, updateActions
from Products.ATContentTypes.interfaces.IATImage import IATImage
from Products.ATContentTypes.types.schemata import ATImageSchema, ATExtImageSchema

from OFS.Image import Image


class ATImage(ATCTContent):
    """An Archetypes derived version of CMFDefault's Image"""

    schema         =  ATImageSchema

    content_icon   = 'image_icon.gif'
    meta_type      = 'ATImage'
    archetype_name = 'AT Image'
    immediate_view = 'image_view'
    default_view   = 'image_view'
    suppl_views    = ()
    newTypeFor     = ('Image', 'Portal Image')
    typeDescription= 'Using this form, you can enter details about the image, and upload\n' \
                     'an image if required.'
    typeDescMsgId  = 'description_edit_image'
    assocMimetypes = ('image/*', )
    assocFileExt   = ('jpg', 'jpeg', 'png', 'gif', )

    __implements__ = ATCTContent.__implements__, IATImage

    security       = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """Display the image, with or without standard_html_[header|footer],
        as appropriate.
        """
        return self.image.index_html(REQUEST, RESPONSE)

    security.declareProtected(CMFCorePermissions.View, 'get_data')
    def get_data(self):
        """CMF compatibility method
        """
        return self.getImage()

    data = ComputedAttribute(get_data, 1)
    
    security.declareProtected(CMFCorePermissions.View, 'get_size')
    def get_size(self):
        """CMF compatibility method
        """
        img = self.getImage()
        return img and img.get_size() or 0
        
    size = ComputedAttribute(get_size, 1)

    security.declareProtected(CMFCorePermissions.View, 'get_content_type')
    def get_content_type(self):
        """CMF compatibility method
        """
        img = self.getImage()
        return img and img.getContentType(self) or '' #'image/jpeg'

    content_type = ComputedAttribute(get_content_type, 1)

    security.declareProtected(CMFCorePermissions.View, 'tag')
    def tag(self, *args, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.image.tag(*args, **kwargs)

registerType(ATImage, PROJECTNAME)


class ATExtImage(ATImage):
    """An Archetypes derived version of CMFDefault's Image with external storage"""

    schema         =  ATExtImageSchema

    content_icon   = 'image_icon.gif'
    meta_type      = 'ATExtImage'
    archetype_name = 'AT Ext Image'
    newTypeFor     = ''
    assocMimetypes = ()
    assocFileExt   = ()

    security       = ClassSecurityInfo()

    def getImage(self, **kwargs):
        """return the image with proper content type"""
        REQUEST=kwargs.get('REQUEST',self.REQUEST)
        RESPONSE=kwargs.get('RESPONSE', REQUEST.RESPONSE)
        field  = self.getField('image') 
        image   = field.get(self, **kwargs)
        ct     = self.getContentType()
        parent = aq_parent(self)
        i      = Image(self.getId(), self.Title(), image, ct)
        return i.__of__(parent)
   
    # make it directly viewable when entering the objects URL
    def index_html(self, REQUEST, RESPONSE):
        self.getImage(REQUEST=REQUEST, RESPONSE=RESPONSE).index_html(REQUEST, RESPONSE)


if HAS_EXT_STORAGE:
    registerType(ATExtImage, PROJECTNAME)
