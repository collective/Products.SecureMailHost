##############################################################################
#
# Copyright (c) 2003 Connexions Projects and Contributors. All Rights Reserved.
#
##############################################################################
""" Basic usergroup tool.

$Id: GroupsToolPermissions.py,v 1.5 2004/05/04 21:48:46 dreamcatcher Exp $
"""

from Products.CMFCore.CMFCorePermissions import setDefaultRoles

#AddRisaModuleEditor = 'Add RISA Module Editor'
#setDefaultRoles(AddRisaModuleEditor, ('Manager', 'Owner', 'Member', 'Anonymous'))

AddGroups = 'Add Groups'
setDefaultRoles(AddGroups, ('Manager',))

ManageGroups = 'Manage Groups'
setDefaultRoles(ManageGroups, ('Manager',))

ViewGroups = 'View Groups'
setDefaultRoles(ViewGroups, ('Manager', 'Owner', 'Member'))

DeleteGroups = 'Delete Groups'
setDefaultRoles(DeleteGroups, ('Manager', ))

SetGroupOwnership = 'Set Group Ownership'
setDefaultRoles(SetGroupOwnership, ('Manager', 'Owner'))
