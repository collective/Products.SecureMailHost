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
# RCS-ID:       $Id: PloneFormMailer.py,v 1.7 2004/08/24 23:52:22 yenzenz Exp $
# Copyright:    (c) 2004 by jens quadrat GbR, Germany
# Licence:      GNU General Public Licence (GPL) Version 2 or later
#------------------------------------------------------------------------------
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.CMFPlone.PloneUtilities import getGlobalTranslationService
from Products.CMFCore.utils import getToolByName

from TALES import TALESLines, TALESString
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from Products.Formulator.Form import ZMIForm

from StringIO import StringIO
from time import strftime

import gpg
from schema import PFMschema
from config import *


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


class PloneFormMailer(BaseContent, TALESLines, TALESString):
    '''
    This product integrates Formulator and CMFFormController. 
    The form will be be mailed to a configureable recipient.
    It is designed to be easily extended and adapted.
    '''
    security = ClassSecurityInfo()
    
    schema  = PFMschema
    actions = actions

    portal_type = meta_type = 'PloneFormMailer' 
    archetype_name = 'Form Mailer'   #this name appears in the 'add' box 
    content_icon = 'formmailer_icon.png'
    allowed_content_types = ()
    global_allow =1
    filter_content_types = 1

    
    def __init__(self, oid, **kwargs):
        BaseContent.__init__(self, oid, **kwargs)
        self.pt = {}
        self.pt = ZopePageTemplate('pt')
        self.subject_expr = None
        
        form = ZMIForm('form', 'PFM Formulator')
        setattr(self, 'form', form)
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
                      'Content-Type': '%s; charset=%s'
                      % (self.getBody_type() or 'text/html',
                         self._site_encoding()),
                      'User-Agent': 'PloneFormMailer for Zope/Plone by jensquadrat.com'}

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

        
def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ('metadata', 'references'):
            a['visible'] = 0
    return fti

registerType(PloneFormMailer)
# end of class PloneFormMailer


