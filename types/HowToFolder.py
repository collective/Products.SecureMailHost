#
# The Plone How-to container.
#
# The main goals of these containers are to restrict the addable types and
# provide a sensible default view out-of-the-box, like the FAQ view.
#

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import HowToFolderSchema
from PHCFolder import PHCFolder


# generate the add method ourselves so we can set the add permission
security = ModuleSecurityInfo('Products.PloneHelpCenter.HowToFolder')
security.declareProtected(ADD_HELP_AREA_PERMISSION, 'addHelpCenterHowToFolder')
def addHelpCenterHowToFolder(self, id, **kwargs):
    o = HelpCenterHowToFolder(id)
    self._setObject(id, o)
    o = getattr(self, id)
    o.initializeArchetype(**kwargs)


class HelpCenterHowToFolder(PHCFolder,OrderedBaseFolder):
    """A simple folderish archetype"""

    content_icon = 'topic_icon.gif'

    schema = HowToFolderSchema
    archetype_name = 'How-to Section'
    meta_type = 'HelpCenterHowToFolder'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterHowTo', )
    
    typeDescription= 'A How-to Section can contain how-to documents.'
    typeDescMsgId  = 'description_edit_howtofolder'

    
    security = ClassSecurityInfo()
    
    actions = (
        {
            'id'          : 'view',
            'name'        : 'View',
            'action'      : 'string:${object_url}/howtofolder_view',
            'permissions' : (CMFCorePermissions.View,)
        },
        {
            'id': 'local_roles',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,)
        },
    )

registerType(HelpCenterHowToFolder, PROJECTNAME)
