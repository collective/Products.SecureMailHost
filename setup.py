#
# PloneTestCase setup
#

# $Id: setup.py,v 1.1 2004/09/11 16:31:22 shh42 Exp $

from Testing import ZopeTestCase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFCalendar')
ZopeTestCase.installProduct('CMFTopic')
ZopeTestCase.installProduct('DCWorkflow')
ZopeTestCase.installProduct('CMFActionIcons')
ZopeTestCase.installProduct('CMFQuickInstallerTool')
ZopeTestCase.installProduct('CMFFormController')
ZopeTestCase.installProduct('GroupUserFolder')
ZopeTestCase.installProduct('ZCTextIndex')
if ZopeTestCase.hasProduct('TextIndexNG'):
    ZopeTestCase.installProduct('TextIndexNG')
if ZopeTestCase.hasProduct('SecureMailHost'):
    ZopeTestCase.installProduct('SecureMailHost')
ZopeTestCase.installProduct('CMFPlone')
ZopeTestCase.installProduct('MailHost', quiet=1)
ZopeTestCase.installProduct('PageTemplates', quiet=1)
ZopeTestCase.installProduct('PythonScripts', quiet=1)
ZopeTestCase.installProduct('ExternalMethod', quiet=1)

from Products.CMFPlone.PloneUtilities import _createObjectByType
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl import getSecurityManager
from Acquisition import aq_base
import time

portal_name = 'plone'
portal_owner = 'portal_owner'
default_policy = 'Default Plone'
default_products = ()
default_user = ZopeTestCase.user_name


def setupPloneSite(id=portal_name, policy=default_policy, products=default_products, quiet=0):
    '''Creates a Plone site and/or quickinstalls products into it.'''
    PortalSetup(id, policy, products, quiet).run()


class PortalSetup:
    '''Creates a Plone site and/or quickinstalls products into it.'''

    def __init__(self, id=portal_name, policy=default_policy, products=default_products, quiet=0):
        self.id = id
        self.policy = policy
        self.products = products
        self.quiet = quiet
        self.with_default_memberarea = 1

    def run(self):
        self.app = ZopeTestCase.app()
        try:
            uf = self.app.acl_users
            if not hasattr(aq_base(self.app), self.id):
                # Add portal owner and log in
                uf.userFolderAddUser(portal_owner, 'secret', ['Manager'], [])
                user = uf.getUserById(portal_owner).__of__(uf)
                newSecurityManager(None, user)
                self._optimize()
                self._setupPloneSite()
            if hasattr(aq_base(self.app), self.id):
                # Log in as portal owner
                user = uf.getUserById(portal_owner).__of__(uf)
                newSecurityManager(None, user)
                self._setupProducts()
        finally:
            noSecurityManager()
            ZopeTestCase.close(self.app)

    def _setupPloneSite(self):
        '''Creates the Plone site.'''
        start = time.time()
        self._print('Adding Plone Site ... ')
        # Add Plone site
        factory = self.app.manage_addProduct['CMFPlone']
        factory.manage_addSite(self.id, create_userfolder=1, custom_policy=self.policy)
        # Precreate default memberarea to speed up the tests
        if self.with_default_memberarea:
            self._setupMemberarea()
        self._commit()
        self._print('done (%.3fs)\n' % (time.time()-start,))

    def _setupProducts(self):
        '''Quickinstalls products into the Plone site.'''
        qi = self.app[self.id].portal_quickinstaller
        for product in self.products:
            if not qi.isProductInstalled(product):
                if qi.isProductInstallable(product):
                    start = time.time()
                    self._print('Adding %s ... ' % (product,))
                    qi.installProduct(product)
                    self._commit()
                    self._print('done (%.3fs)\n' % (time.time()-start,))
                else:
                    self._print('Adding %s ... NOT INSTALLABLE\n' % (product,))

    def _optimize(self):
        '''Applies optimizations to the PloneGenerator.'''
        _optimize()

    def _setupMemberarea(self):
        '''Creates the default user's memberarea.'''
        _createHomeFolder(self.app[self.id], default_user)
    
    def _commit(self):
        '''Commits the transaction.'''
        get_transaction().commit()

    def _print(self, msg):
        '''Prints msg to stderr.'''
        if not self.quiet:
            ZopeTestCase._print(msg)


def _createHomeFolder(portal, member_id):
    '''Creates the folders comprising a memberarea.'''
    membership = portal.portal_membership
    members = membership.getMembersFolder()
    # Punt if the home folder already exists
    if not hasattr(aq_base(members), member_id):
        # Create home folder
        _createObjectByType('Folder', members, id=member_id)
        # Create personal folder
        home = membership.getHomeFolder(member_id)
        _createObjectByType('Folder', home, id=membership.personal_id)
        # Uncatalog personal folder
        personal = membership.getPersonalFolder(member_id)
        personal.unindexObject()


def _takeOwnershipOfHomeFolder(portal, member_id):
    '''Takes ownership of a memberarea.'''
    membership = portal.portal_membership
    # Get member
    member = portal.acl_users.getUserById(member_id)
    if member is None:
        raise ValueError, 'Member %s does not exist' % member_id
    if not hasattr(member, 'aq_base'):
        member = member.__of__(portal.acl_users)
    # Take ownership of home folder
    home = membership.getHomeFolder(member_id)
    home.changeOwnership(member)
    home.__ac_local_roles__ = None
    home.manage_setLocalRoles(member_id, ['Owner'])
    # Take ownership of personal folder
    personal = membership.getPersonalFolder(member_id)
    personal.changeOwnership(member)
    personal.__ac_local_roles__ = None
    personal.manage_setLocalRoles(member_id, ['Owner'])


def _optimize():
    '''Significantly reduces portal creation time.'''
    # Don't compile expressions on creation
    def __init__(self, text):
        self.text = text
    from Products.CMFCore.Expression import Expression
    Expression.__init__ = __init__
    # Don't clone actions but convert to list only
    def _cloneActions(self):
        return list(self._actions)
    from Products.CMFCore.ActionProviderBase import ActionProviderBase
    ActionProviderBase._cloneActions = _cloneActions
    # Don't setup default directory views
    def setupDefaultSkins(self, p):
        from Products.CMFCore.utils import getToolByName
        ps = getToolByName(p, 'portal_skins')
        ps.manage_addFolder(id='custom')
        ps.addSkinSelection('Basic', 'custom')
    from Products.CMFPlone.Portal import PloneGenerator
    PloneGenerator.setupDefaultSkins = setupDefaultSkins
    # Don't setup default Members folder
    def setupMembersFolder(self, p):
        pass
    PloneGenerator.setupMembersFolder = setupMembersFolder
    # Don't setup Plone content (besides Members folder)
    def setupPortalContent(self, p):
        p.invokeFactory('Large Plone Folder', id='Members')
        p.portal_catalog.unindexObject(p.Members)
    PloneGenerator.setupPortalContent = setupPortalContent
