#------------------------------------------------------------------------------
# Name:         PloneFormMailer.py
# Purpose:      This product integrates Formulator and CMFFormController. 
#               The form will be be mailed to a configureable recipient.
#               It is designed to be easily extended and adapted. 
#
# Author:       Jens Klein <jens.klein@jensquadrat.de>
# generated by: ArchGenXML Version 0.9.14 http://sf.net/projects/archetypes/
#
# Created:      Sun Jan 25 22:09:22 2004
# RCS-ID:       $Id: PloneFormMailer.py,v 1.3 2004/05/28 08:36:18 yenzenz Exp $
# Copyright:    (c) 2004 by jens quadrat GbR, Germany
# Licence:      GNU General Public Licence (GPL) Version 2 or later
#------------------------------------------------------------------------------
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.CMFPlone.PloneUtilities import getGlobalTranslationService
from Products.CMFCore.utils import getToolByName

from TALES import TALESLines, TALESString
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from StringIO import StringIO
from time import strftime

import gpg


default_mailtemplate_subject = \
"""string:PloneFormMailer"""

default_mailtemplate_body = \
"""<tal:block i18n:domain="PloneFormMailer" 
           tal:define="form here/form;
                       groups form/get_groups;">
<html>
<body>
<pre tal:content="here/getBody_pre" />
<pre tal:content="options/prepend" />

<tal:block tal:repeat="group groups">
  <pre tal:condition="python:group!='Default'" tal:content="group" />
  <tal:block tal:repeat="field python:form.get_fields_in_group(group)">
    <tal:block tal:condition="python:here.REQUEST.get('field_%s' % field.id, '')">
      <pre tal:content="python:'['+field.title()+']'" />
      <pre tal:content="python:here.REQUEST.get('field_%s' % field.id, '')" /><br />
    </tal:block>
  </tal:block>
</tal:block>

<pre tal:content="options/append" />
<pre tal:content="here/getBody_post" />
<pre tal:content="here/getFooter" /></tal:block>
</body>
</html>"""

class PloneFormMailer(BaseFolder, TALESLines, TALESString):
    '''
    This product integrates Formulator and CMFFormController. 
    The form will be be mailed to a configureable recipient.
    It is designed to be easily extended and adapted.
    '''
    security = ClassSecurityInfo()
    portal_type = meta_type = 'PloneFormMailer' 
    archetype_name = 'PloneFormMailer'   #this name appears in the 'add' box 
    schema=BaseSchema  + Schema((
        #name of the recipient
        StringField('recipient_name',
            widget=StringWidget(description = 'The full name of the recipient '
                'of the mailed form. TALES Expression. If you don\'t know '
                'TALES expressions just write \'string:YOURTEXT\'.',
                description_msgid = "help_formmailer_recipient_fullname",
                label = 'Recipient full name',
                label_msgid = "label_formmailer_recipient_fullname",                 
            ),
            validators=('talesvalidator',),
            schemata='Mail Header',
            required=1,
        ),
        
        #e-mail adress of the recipient of the form-data
        StringField('recipient_email',
            widget=StringWidget(description = 'The recipients e-mail address. '
                'TALES Expression. If you don\'t know TALES expressions just '
                'write \'string:YOURTEXT\'.',
                description_msgid = "help_formmailer_recipient_email",
                label = 'Recipient e-mail address',
                label_msgid = "label_formmailer_recipient_email",                 
            ),                                
            schemata='Mail Header',
            validators=('talesvalidator',),
            required=1
        ),

        #additional recipients email-adresses by CC
        LinesField('cc_recipients',
            widget=LinesWidget(
                description = 'E-mail addresses which receive a carbon copy. '
                'TALES Expression. If you don\'t know TALES expressions just '
                'write \'string:YOURTEXT\'.',
                description_msgid = "help_formmailer_cc_recipients",
                label = 'Cc recipients',
                label_msgid = "label_formmailer_cc_recipients",
            ),
            schemata='Mail Header',
            validators=('talesvalidator',)                   
        ),
        
        
        #additional recipients email-adresses by BCC
        LinesField('bcc_recipients',
            widget=LinesWidget(
                description = 'E-mail addresses which receive a blind carbon copy. '
                'TALES Expression. If you don\'t know TALES expressions just '
                'write \'string:YOURTEXT\'.',
                description_msgid = "help_formmailer_bcc_recipients",
                label = 'Bcc recipients',
                label_msgid = "label_formmailer_bcc_recipients",
            ),
            schemata='Mail Header',
            validators=('talesvalidator',)
        ),
        
        #header lines in formatting KEY: VALUE
        LinesField('additional_headers',
            widget=LinesWidget(description = 'Additional e-mail-header lines. '
                'Only fill in if you aware of RFC822.',
                description_msgid = "help_formmailer_additional_headers",
                label = 'Additional headers',
                    label_msgid = "label_formmailer_additional_headers",
            ),                                
            schemata='Mail Header'
        ),
        
        #subject of the message
        StringField('subject',
            default = default_mailtemplate_subject,
            widget=StringWidget(description = 'Subject line of message. '
                'TALES Expression. If you don\'t know TALES expressions just '
                'write \'string:YOURTEXT\'.',
                description_msgid = "help_formmailer_subject",
                label = 'Subject',
                label_msgid = "label_formmailer_subject",                 
            ),                                
            validators=('talesvalidator',),
            schemata='Mail Message'
        ),
        
        #text introduces the body before field-listing starts
        TextField('body_pre',
            widget=TextAreaWidget(description = 'Text prepended to fields-list '
                'in mail-body',
                description_msgid = "help_formmailer_body_pre",
                label = 'Body (prepended)',
                label_msgid = "label_formmailer_body_pre",
            ),
            schemata='Mail Message'
        ),

        #text in e-mail after field list
        TextField('body_post',
            widget=TextAreaWidget(description = 'Text appended to fields-list '
                'in mail-body',
                description_msgid = "help_formmailer_body_post",
                label = 'Body (appended)',
                label_msgid = "label_formmailer_body_post",
            ),
            schemata='Mail Message'
        ),

        #text used as the footer of e-mail (do not include delimiter)
        TextField('body_footer',
            widget=TextAreaWidget(description = 'Text used as the mail-footer '
                'at bottom, delimited from the other body by "-- <newline>".',
                description_msgid = "help_formmailer_body_footer",
                label = 'Body (footer)',
                label_msgid = "label_formmailer_body_footer",
            ),
                                
            schemata='Mail Message'
        ),

        #text introduces the body before field-listing starts
        TextField('body_pt',
            default = default_mailtemplate_body, 
            default_content_type='application/xml+xhtml',
            default_output_type='text/plain',
            widget=TextAreaWidget(description = 'This is a Zope Page Template '
                'used for rendering of the mail-body. You don\'t need to modify '
                'it, but if you know Zope\'s TAL (Template Attribute Language) '
                'you have the full power to customize your outgoing mails.',
                description_msgid = "help_formmailer_body_pt",
                label = 'Mail-Body Template',
                label_msgid = "label_formmailer_body_pt",
                rows = 30,
            ),
            validators=('zptvalidator',),
            schemata='Template'
        ),        
        
##        #strip html?
##        BooleanField('body_pt_striphtml',
##            default = 0,
##            widget=BooleanWidget(description = 'Strip HTML tags from rendered '
##                'mail template. ',
##                description_msgid = "help_formmailer_body_pt_strip",
##                label = 'Strip HTML?',
##                label_msgid = "label_formmailer_body_pt_strip",
##            ),
##            schemata='Template'
##        ),                
        
        #text prepended to list of fields
        TextField('form_pre',
            widget=RichWidget(description = "Text prepended to the web-form.",
                description_msgid = "help_formmailer_form_pre",
                label = "Text (prepended)",
                label_msgid = "label_formmailer_form_pre",
                rows = 12
            ),
            default_content_type='text/structured',
            allowable_content_types=('text/structured',
                                    'text/restructured',
                                    'text/html',
                                    'text/plain'),
            schemata='Form',
            default_output_type='text/html'
        ),
        #text appended to list of fields
        TextField('form_post',
            widget=RichWidget(description = "Text appended to the web-form.",
                description_msgid = "help_formmailer_form_post",
                label = "Text (appended)",
                label_msgid = "label_formmailer_form_post",
                rows = 12),                                
            default_content_type='text/structured',
            allowable_content_types=('text/structured',
                                    'text/restructured',
                                    'text/html',
                                    'text/plain'),
            schemata='Form',
            default_output_type='text/html'
        ),

        
        #label for send button
        LinesField('form_buttons',
            widget=LinesWidget(description = 'Definition of the buttons. '
                'format: value|name|type|css-class.',
                description_msgid = "help_formmailer_form_buttons",
                label = 'Buttons',
                label_msgid = "label_formmailer_form_button_submit",                 
            ),
            default=("""Submit|submit|submit|context""",
                     """Reset|reset|reset|standalone"""),
            schemata='Form',
            required=1,

        ),
        #gpg key-id
        StringField('gpg_keyid',
            widget=StringWidget(description = 'Give your key-id, e-mail or '
                'whatever works to match a public key from current keyring. '
#                'keyserver or given public key. '
                'It will be used to encrypt the '
                'message body. You need to have a working "GNU Privacy Guard" binary '
                'installed on the machine running zope! Test this feature before going public!',
                description_msgid = "help_formmailer_key_id",
                label = 'Key-Id',
                label_msgid = "label_formmailer_key_id",                 
            ),                                
            schemata='Encryption'
        ),        
        
##        #gpg keyserver
##        StringField('gpg_keyserver',
##            widget=StringWidget(description = 'Name a Keyserver, where the '
##                'above key can be found. Not needed if it is already in current'
##                'keyring or a public key is given',
##                description_msgid = "help_formmailer_gpg_keyserver",
##                label = 'Keyserver',
##                label_msgid = "label_formmailer_gpg_keyserver",                 
##            ),                                
##            schemata='Encryption'
##        ),
##        
##
##        #gpg public key
##        TextField('gpg_public',
##            widget=TextAreaWidget(description = 'Paste your GPG/PGP public key in '
##                'here.',
##                description_msgid = "help_formmailer_gpg_public",
##                label = "Public Key",
##                label_msgid = "label_formmailer_gpg_public",
##                rows = 12),                                
##            default_content_type='text/plain',
##            allowable_content_types=('text/plain'),
##            schemata='Encryption',
##            default_output_type='text/html'
##        ),        
        
        #action to be executed after successful validation
        StringField('cpyaction',
            widget=StringWidget(description = 'Set an alternate controller '
                'python script (cpy). Change this setting only if you exact '
                'now what you are doing. Left it blank for default behaviour.',
                description_msgid = "help_formmailer_cpyaction",
                label = 'Controller Script',
                label_msgid = "label_formmailer_cpyaction",                 
            ),                                
            schemata='Controller'
        ),        
        
        #title of 'Sent Response'
        StringField('sent_title',
            widget=StringWidget(description = 'The title of the page displayed '
                'after successful sending. If left blank the primary title '
                'field is used.',
                description_msgid = "help_formmailer_sent_title",
                label = 'Title (sent page)',
                label_msgid = "label_formmailer_sent_title",                 
            ),
            schemata='Sent Response'
        ),
        
        #message for 'Sent Response'
        TextField('sent_message',
            widget=RichWidget(description = 'The message of the page displayed '
                'after successful sending.',
                description_msgid = "help_formmailer_sent_msg",
                label = 'Message (sent page)',
                label_msgid = "label_formmailer_sent_msg",                 
            ),                                
            default_content_type='text/structured',
            allowable_content_types=('text/structured',
                                    'text/restructured',
                                    'text/html',
                                    'text/plain'),
            schemata='Sent Response',
            default_output_type='text/html'
        ),
        
        #ignore sent_title, sent_message and redirect to another page
        StringField('sent_redirect',
            widget=StringWidget(description = 'Redirect to a custom set page '
                'is possible too (instead of standard sent page).'
                'TALES Expression. If you don\'t know TALES expressions just '
                'write \'string:YOURTEXT\'.',
                description_msgid = "help_formmailer_sent_redirect",
                label = 'Redirect to (sent)',
                label_msgid = "label_formmailer_sent_redirect",                 
            ),                                
            validators=('talesvalidator',),
            schemata='Sent Response'
        ),
    ),
    )

    def __init__(self, oid, **kwargs):
        BaseFolder.__init__(self, oid, **kwargs)
        self.pt = {}
        self.pt = ZopePageTemplate('pt')
        self.subject_expr = None

    def manage_afterAdd(self, item, container):
        '''
        add a formulator with standard set up to the archetype.
        add a mail template with standard setup to the archetype.
        '''          
        BaseFolder.manage_afterAdd(self,item, container)
        if not 'form' in self.objectIds():
            # add a Formulator form
            self.manage_addProduct['Formulator'].manage_add('form', 'Formulator')
            self.form.manage_addField('fullname','fullname','StringField')
            self.form.manage_addField('email','e-mail','EmailField')
            self.form.manage_addField('message','message','TextAreaField')
            

    # custom setters ##########################################################

    def setExpressionsField(self, fname, value, **kwargs):
        self.getField(fname).set(self, value)
        self.compileExpressions(fname)

    def setExpressionField(self, fname, value, **kwargs):
        self.getField(fname).set(self, value)
        self.compileExpression(fname)

    def setCc_recipients(self, value, **kwargs):
        self.setExpressionsField('cc_recipients', value, **kwargs)

    def setBcc_recipients(self, value, **kwargs):
        self.setExpressionsField('bcc_recipients', value, **kwargs)

    def setRecipient_email(self, value, **kwargs):
        self.setExpressionField('recipient_email', value, **kwargs)

    def setRecipient_name(self, value, **kwargs):
        self.setExpressionField('recipient_name', value, **kwargs)

    def setSubject(self, value, **kwargs):
        self.setExpressionField('subject', value, **kwargs)
        
    def setBody_pt(self, value, **kwargs):
        self.getField('body_pt').set(self, value, **kwargs)
        self.pt.write(self.getField('body_pt').get(self))        
        
    # special processings #####################################################
    
    def getButtons(self):
        buttons=[]
        for buttondef in self.getForm_buttons():
            button= []
            [button.append(s.strip()) for s in buttondef.split('|')]
            buttons.append(button)
        return buttons

    # send_form ###############################################################
       
    def get_mail_text(self, prepend='', append='', **kwargs):
        '''\
        get header and body of e-mail as text (string)

        Keyword arguments:
        ua_description -- alternate user agent description used in header and as 
                          default footer
        '''
        
        mt_sio = StringIO()
        
        (headerinfo, additional_headers, body) = self.get_header_body_tuple( \
                                                    prepend, 
                                                    append, 
                                                    **kwargs)
        # write header
        for key, value in headerinfo.items():
            print >> mt_sio, key + ': ' + value

        # write additional header
        for a in additional_headers:
            print >> mt_sio, a
            
        # build complete text
        mailtext = mt_sio.getvalue() + '\n' + body
        return mailtext
    
    def get_mail_body(self, prepend='', append='', hidefields=[], **kwargs):
        ''' returns the mail-body with footer '''
        
        if kwargs.has_key('request'):
            request = kwargs['request']
        else:
            request = self.REQUEST   

        UA_DESCRIPTION = \
            'PloneFormMailer (send web forms via e-mail using Zope/Plone)'

        if kwargs.has_key('ua_description'):
            UA_DESCRIPTION = kwargs['ua_description']
            
        if type(hidefields)!=type([]):
            hidefields=[hidefields]            

        info = {
            'prepend': prepend,
            'append':  append,
            'useragent': UA_DESCRIPTION,
            'hidefields': hidefields,            
        }

        body = self.pt.pt_render(extra_context={'options': info})
        
        if kwargs.has_key('encryption'):
            encryption =  kwargs['encryption']
        else:
            encryption = 1
        encryption = encryption and self.getGpg_keyid() 
            
        # check if encryption needed.
        keyid=self.getGpg_keyid() 
        if encryption:
            # XXX :-( TODO 
            # check if keyid exists in keyring
            # else if keyserver is given try to get it from keyserver
            # else if public_key is given try to import it
            # else
            # print "!!! PloneFormMailer",self.id,": gpg encryption failed. A key is given but invalid."
            # if not failed 
            gpgobj = gpg.gpg_subprocess()
            bodygpg=gpgobj.encrypt(body,keyid)
            if bodygpg.strip():
                body=bodygpg
                        
        return body

    def getFooter(self, **kwargs):

        UA_DESCRIPTION = \
            'PloneFormMailer (send web forms via e-mail using Zope/Plone)'

        if kwargs.has_key('ua_description'):
            UA_DESCRIPTION = kwargs['ua_description']

        if self.getBody_footer():
            return '-- \n'+self.getBody_footer()
        else:
            return '-- \n'+UA_DESCRIPTION + '\n\n'+\
                'brought to you by jens quadrat GbR, Germany\n'+\
                'http://jensquadrat.de/    http://plone.org/'
                

    def get_header_body_tuple(self, prepend='', append='', **kwargs):
        '''\
        returns header and body of e-mail as an 3-tuple:
        (header, additional_header, body)
        header is a dictionary, additional header is a list, body is a StringIO

        Keyword arguments:
        ua_description -- alternate user agent description used in header and as 
                          default footer
        request -- (optional) alternate request object to use
        '''
        
        if kwargs.has_key('request'):
            request = kwargs['request']
        else:
            request = self.REQUEST

        # this is a tuple if empty, dunno why

        header = StringIO()
        
        body = self.get_mail_body(prepend, append, '', **kwargs)
        
        from_addr = None        
        
        subject = self.getEvaluatedExpression('subject') or '(no subject)'

        for field in self.form.get_fields():
            if not getattr(field, 'sub_form', None):
                value = request.get('field_%s' % field.id, '')
                if value:
                    if field.id == 'email':
                        from_addr = value
                    if field.id == 'subject':
                        subject += value
            
##        subject = subject.strip() + ' '
##        if self.getSubject_add_timestamp():
##            subject+=' '+strftime('%c')

        from_addr = from_addr or \
                    self.portal_properties.site_properties.email_from_address
        to = '%s <%s>' % (self.getEvaluatedExpression('recipient_name'),
                          self.getEvaluatedExpression('recipient_email'))
        
        headerinfo = {'To': to,
                      'From': from_addr,
                      'Subject': subject,
                      'Content-Type': 'text/html; charset=%s'
                      % self._site_encoding(),
                      'User-Agent': 'PloneFormMailer for Zope/Plone by jens quadrat GbR'}

        # CC
        addrs = ['<%s>' % addr
                 for addr in self.getEvaluatedExpressions('cc_recipients')]
        headerinfo['Cc'] = ','.join(addrs)

        # BCC
        addrs = ['<%s>' % addr
                 for addr in self.getEvaluatedExpressions('bcc_recipients')]
        headerinfo['Bcc'] = ','.join(addrs)
        
        # return 3-Tuple
        return (headerinfo, self.getAdditional_headers(), body)
        

    # send_form ###############################################################

    def send_form(self, prepend='', append='', **kwargs):
        '''\
        send form

        Keyword arguments:
        ua_description -- alternate user agent description used in header and as 
                          default footer
        '''
        
        mailtext=self.get_mail_text(prepend, append, **kwargs)
               
        host = self.MailHost
        host.send(mailtext)    


    # translation and encodings ###############################################

    def _site_encoding(self):
        site_props = self.portal_properties.site_properties
        return site_props.default_charset or 'UTF-8'


    # factory type information ################################################

    factory_type_information={
        'allowed_content_types':() ,
        'content_icon':'formmailer_icon.png',
        #'immediate_view':'formmailer',
        'global_allow':1,
        'filter_content_types':1,
        }

        
    actions=(
        

           {'action':      'string:${object_url}/formmailer',
            'category':    'object',
            'id':          'view',
            'name':        'View',
            'permissions': ('View',)},
          

           {'action':      'string:${object_url}/form/manage',
            'category':    'object',
            'id':          'modifyformulatorform',
            'name':        'Modify Form (ZMI)',
            'permissions': ('Modify portal content',)},
          

          )
        
def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ('metadata', 'references'):
            a['visible'] = 0
    return fti

registerType(PloneFormMailer)
# end of class PloneFormMailer

