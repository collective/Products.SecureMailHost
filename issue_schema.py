"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: issue_schema.py,v 1.5 2003/09/10 04:32:58 ajung Exp $
"""

from Products.Archetypes.public import BaseSchema, Schema, DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget

schema = BaseSchema +  Schema((
    StringField('description',
                searchable=1,
                schemata='issuedata'
                ),
    StringField('solution',
                searchable=1,
                schemata='issuedata'
                ),
    StringField('progress_hours_estimated',
                schemata='progress'
                ),
    StringField('progress_hours_needed',
                schemata='progress'
                ),
    StringField('progress_percent_done',
                schemata='progress'
                ),
    # do not remove 'contact_name'
    StringField('contact_name',
                searchable=1,
                required=1,
                schemata='contact'
                ),
    # do not remove 'contact_email'
    StringField('contact_email',
                searchable=1,
                required=1,
                schemata='contact',
                validators=('isEmail',)
                ),
    StringField('contact_address',
                searchable=1,
                schemata='contact'
                ),
    StringField('contact_phone',
                searchable=1,
                schemata='contact'
                ),
    StringField('contact_fax',
                searchable=1,
                schemata='contact'
                ),
    ))
