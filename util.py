"""
PloneCollectorNG - A Plone-based bugtracking system

(C) 2002-2004, Andreas Jung

ZOPYX Software Development and Consulting Andreas Jung
Charlottenstr. 37/1
D-72070 T�bingen, Germany
Web: www.zopyx.com
Email: info@zopyx.com 

License: see LICENSE.txt

$Id: util.py,v 1.23 2004/11/14 15:59:53 ajung Exp $
"""

import os, urllib
from Products.Archetypes.public import DisplayList

package_home = os.path.dirname(__file__)


def getUserName():
    """ return user name """
    from AccessControl import getSecurityManager
    return getSecurityManager().getUser().getUserName()


def addLocalRole(obj, userid, role):
    """ add a local role for a user """
    roles = list(obj.get_local_roles_for_userid(userid))
    if role not in roles:
        roles.append(role)
        obj.manage_setLocalRoles(userid, roles)


def removeLocalRole(obj, userid, role):
    """ remove a local role from obj """
    roles = list(obj.get_local_roles_for_userid(userid))
    roles.remove(role)
    if roles:
        obj.manage_setLocalRoles(userid, roles)
    else:
        obj.manage_delLocalRoles([userid])


def adjustLocalRoles(obj, userids, role):
    """ adjust local roles for a role and a list of users """

    already = []
    changed = 0
    for u in obj.users_with_local_role(role):
        if u in userids:
            already.append(u)
        else:
            changed = 1
            removeLocalRole(obj, u, role)
    for u in userids:
        if u not in already:
            changed = 1
            addLocalRole(obj, u, role)
    return changed


def isValidEmailAddress(email):
    """ validate an email address """

    #XXX: Replace this with a better implementation
    #XXX: and log invalid addresses

    at = email.find('@')
    pt = email.find('.')
    # Minimal lenght must be 8
    if len(email) <= 7 :
        return False
    # We must have an @ but not first and not last
    if at == -1 or at == 0 or email[-1] == '@':
        return False
    # Same applies for the point
    if pt == -1 or pt == 0 or email[-1] == '.':
        return False
    # Only one @ is valid
    if email.find('@',at+1) > -1:
        return False
    # @ and . cannot be together
    if email[at-1] == '.' or email[at+1] == '.':
        return False
    # subdomain must have at least 2 letters
    if email[at+2] == '.':
        return False
    # no spaces allowed
    if email.find(' ') > -1:
        return False
    return True


def remove_dupes(lst):
    """ remove dupes from a list """

    ret = []
    for l in lst:
        if not l in ret:
            ret.append(l)
    return ret 


def lists_eq(l1, l2):
    """ compare two lists """   
    l1 = list(l1); l2 = list(l2)
    l1.sort(); l2.sort()
    return l1==l2


def redirect(RESPONSE, dest, msg=None,**kw):
    
    if RESPONSE is not None:    
        url = dest + "?"
        if msg:
            url += "portal_status_message=%s&" % urllib.quote(msg)
        if kw:
            url += '&'.join(['%s=%s' % (k, urllib.quote(v)) for k,v in kw.items()])
        RESPONSE.redirect(url) 


def safeGetProperty(userobj, property, default=None):
    """Defaulting user.getProperty(), allowing for variant user folders."""
    try:
        if not hasattr(userobj, 'getProperty'):
            return getattr(userobj, property, default)
        else:
            return userobj.getProperty(property, default)
    except:
        # We can't just itemize the possible candidate exceptions because one
        # is a string with spaces, which isn't interned and hence object id
        # won't match.  Sigh.
        import sys
        exc = sys.exc_info()[0]
        if (exc == 'Property not found'
            or isinstance(exc, TypeError)
            or isinstance(exc, AttributeError)
            or isinstance(exc, LookupError)):
            try:
                # Some (eg, our old LDAP user folder) support getProperty but
                # not defaulting:
                return userobj.getProperty(property)
            except:
                return default
        else:
            raise

def encrypt(text, key):
    """ AES Encryption """
    try:
        from Crypto.Cipher import AES
    except ImportError:
        from zLOG import LOG, ERROR
        LOG('plonecollectorng', ERROR, 'PyCrypto (www.amk.ca/python/code/crypto) is required')
        raise

    obj = AES.new(key, AES.MODE_ECB)

    if len(text) % 16 != 0: # padding
        text += ' ' *(16-(len(text)%16)) 
    return obj.encrypt(text)


def decrypt(text, key):
    """ AES Decryption """
    try:
        from Crypto.Cipher import AES
    except ImportError:
        from zLOG import LOG, ERROR
        LOG('plonecollectorng', ERROR, 'PyCrypto (www.amk.ca/python/code/crypto) is required')
        raise
    
    obj = AES.new(key, AES.MODE_ECB)
    return obj.decrypt(text)
   

def readLinesFromDisk(fname):
    fname = os.path.join(package_home, 'data', fname)
    if not os.path.exists(fname):
        raise IOError, 'File not found: %s' % fname
    lines = open(fname).readlines()
    lines = [l.strip() for l in lines]
    lines = filter(None, lines)
    return lines


def DisplayListFromFile(fname):
    lines = readLinesFromDisk(fname)
    return DisplayList(zip(lines, lines)) 

