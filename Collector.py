
from Globals import InitializeClass
from AccessControl import getSecurityManager, ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CatalogTool import CatalogTool
from BTrees.OOBTree import OOBTree
from Products.BTreeFolder2 import CMFBTreeFolder
from Products.Archetypes.public import BaseFolder, registerType

from Transcript import Transcript, TranscriptEntry
from config import ManageCollector, AddCollectorIssue, AddCollectorIssueFollowup
from config import IssueWorkflowName
import util
import collector_schema

class Collector(BaseFolder):
    """ PloneCollectorNG """

    schema = collector_schema.schema

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'pcng_view',
        'permissions': (CMFCorePermissions.View,)
        },
        {'id': 'history',
        'name': 'History',
        'action': 'pcng_history',
        'permissions': (ManageCollector,)
        },
        {'id': 'staff',
        'name': 'Staff',
        'action': 'pcng_staff',
        'permissions': (ManageCollector,)
        },
        {'id': 'issueproperties',
        'name': 'Issue properties',
        'action': 'pcng_issue_properties',
        'permissions': (ManageCollector,)
        },
        {'id': 'notifications',
        'name': 'Notifications',
        'action': 'pcng_notifications',
        'permissions': (ManageCollector,)
        },
        )

    __ac_roles__ = ('Manager', 'TrackerAdmin', 'Supporter', 'Reporter')
    security = ClassSecurityInfo()

    def __init__(self, oid, **kwargs):
        BaseFolder.__init__(self, oid, **kwargs)
        self._supporters = self._managers = self._reporters = []
        self._notification_emails = OOBTree()
        self.transcript = Transcript()
        self._setup_collector_catalog()
        self.transcript.addComment('Tracker created')

        # setup roles 
        username = util.getUserName()
        for role in ('Manager', 'TrackerAdmin', 'Owner'):
            util.add_local_role(self, username, role)

    def _setup_collector_catalog(self):
        """Create and situate properly configured collector catalog."""
        catalog = PloneCollectorNGCatalog()
        self._setObject(catalog.id, catalog)
        catalog = catalog.__of__(self)

    def pre_validate(self, REQUEST, errors):
        """ Hook to perform pre-validation actions. We use this
            hook to log changed properties to the transcript.
        """

        te = TranscriptEntry()
        for name in REQUEST.form.keys():
            new = REQUEST.get(name, None)
            old = getattr(self, name, None)
            if old:
                if old != new:
                    te.addChange(name, old, new)

        self.transcript.add(te)
        self.transcript._p_changed = 1

    ######################################################################
    # Staff handling
    ######################################################################

    security.declareProtected(ManageCollector, 'getSupporters')
    def getSupporters(self): return self._supporters

    security.declareProtected(ManageCollector, 'getManagers')
    def getManagers(self): return self._managers

    security.declareProtected(ManageCollector, 'getReporters')
    def getReporters(self): return self._reporters

    security.declareProtected(ManageCollector, 'getTrackerUsers')
    def getTrackerUsers(self):   
        """ return a list of dicts where every item of the list
            represents a user and the dict contain the necessary
            informations for the presentation.
        """

        l = []
        names = self._managers + self._supporters + self._reporters + self.acl_users.getUserNames()
        for name in util.remove_dupes(names):
            d = {}
            d['username'] = name; d['roles'] = []
            if name in self._managers: d['roles'].append('TrackerAdmin')
            if name in self._supporters: d['roles'].append('Supporter')
            if name in self._reporters: d['roles'].append('Reporter')
            l.append(d)
        return l

    security.declareProtected(ManageCollector, 'set_staff')
    def set_staff(self, reporters=[], managers=[], supporters=[], RESPONSE=None):
        """ set the staff """

        reporters.sort(); managers.sort(); supporters.sort()

        te = TranscriptEntry()
        te.addChange('managers', self._managers, managers)
        te.addChange('supporters', self._supporters, supporters)
        te.addChange('reporters', self._reporters, reporters)

        self._managers = managers
        self._reporters = reporters
        self._supporters = supporters
        self._adjust_staff_roles()

        self.transcript.add(te)
        self.transcript._p_changed = 1

        if RESPONSE is not None: RESPONSE.redirect('pcng_view?portal_status_message=Your%20changes%20has%20been%20saved')

    def _adjust_staff_roles(self):
        """ A djust local-role assignments to track staff roster settings.
            Ie, ensure: only designated supporters and managers have 'Reviewer'
            local role, only designated managers have 'Manager' local role.
        """
        if not self._managers:
            self._managers = [getSecurityManager().getUser().getUserName()]
        util.users_for_local_role(self, self._managers, 'TrackerAdmin')
        util.users_for_local_role(self, self._supporters, 'Supporter')
        util.users_for_local_role(self, self._reporters, 'Reporter')

    def _adjust_participation_mode(self):
        """Set role privileges according to participation mode."""

        target_roles = ('Supporter','TrackerAdmin','Reporter', 'Manager', 'Owner')

        if self.participation_mode == 'authenticated':
            target_roles = target_roles + ('Authenticated', )
        elif self.participation_mode == 'anyone':
            target_roles = target_roles + ('Authenticated', 'Anonymous')

        self.manage_permission(AddCollectorIssue,
                               roles=target_roles,
                               acquire=0)

        self.manage_permission(AddCollectorIssueFollowup,
                               roles=target_roles,
                               acquire=0)

    ######################################################################
    # Notifications
    ######################################################################

    security.declareProtected(ManageCollector, 'set_notification_emails')
    def set_notification_emails(self, notifications, RESPONSE=None):
        """ set the email addresses for notifications when a workflow
            state changes.
            
            'notifications' -- record where the keys are the names of the
                        states and the values are lists of email addresses
        """

        te = TranscriptEntry()

        for state in notifications.keys():
            emails = getattr(notifications, state)
            emails = [e.strip() for e in emails if e.strip()]
            for email in emails:
                if not util.isValidEmailAddress(email):
                    raise ValueError('Invalid email address: %s' % email)

            te.addChange('notifications', self._notification_emails.get(state, []), emails)
            self._notification_emails[state] = emails

        self.transcript.add(te)
        self.transcript._p_changed = 1
        if RESPONSE is not None: RESPONSE.redirect('pcng_view?portal_status_message=Your%20changes%20has%20been%20saved')

    security.declareProtected(ManageCollector, 'getNotificationsForState')
    def getNotificationsForState(self, state):
        """ return a of emails addresses that correspond to
            the given state.
        """
        return self._notification_emails.get(state, [])

    security.declareProtected(ManageCollector, 'issue_states')
    def issue_states(self):
        """ return a list of all related issue workflow states """

        states = getattr(self.portal_workflow, IssueWorkflowName).states._mapping.keys()
        states.sort()
        return states


registerType(Collector)


class PloneCollectorNGCatalog(CatalogTool):
    """ catalog for collector issues """

    id = 'pcng_catalog'
    meta_type = 'PloneCollectorNG Catalog'
    portal_type = 'PloneCollectorNG Catalog'

    def enumerateIndexes(self):
        standard = CatalogTool.enumerateIndexes(self)
        custom = (('status', 'FieldIndex'),
                  ('topic', 'FieldIndex'),
                  ('subtopic', 'FieldIndex'),
                  ('classification', 'FieldIndex'),
                  ('importance', 'FieldIndex'),
                  ('security_related', 'FieldIndex'),
                  ('confidential', 'FieldIndex'),
                  ('submitter_id', 'FieldIndex'),
                  ('submitter_email', 'FieldIndex'),
                  ('version_info', 'TextIndex'),
                  ('assigned_to', 'KeywordIndex'),
                  ('deadline', 'FieldIndex'),
                  ('progress', 'FieldIndex'),
                  ('getId', 'FieldIndex'),
                  )
        custom = tuple([col for col in custom if col not in standard])
        return standard + custom

    def enumerateColumns( self ):
        """Return field names of data to be cached on query results."""
        standard = CatalogTool.enumerateColumns(self)
        custom = ('id', 'status', 'submitter_id', 'topic', 'subtopic', 'classification',
                  'importance', 'security_related', 'confidential', 'version_info',
                  'assigned_to', 'deadline', 'progress', 'getId',
                  )
        custom = tuple([col for col in custom if col not in standard])
        return standard + custom

InitializeClass(PloneCollectorNGCatalog)
