"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Base.py,v 1.3 2003/11/29 07:20:14 ajung Exp $
"""

from Globals import InitializeClass
from Products.Archetypes.BaseBTreeFolder import BaseBTreeFolder

class Base(BaseBTreeFolder):
    """ base class for collector/issues """

    def SchemataNames(self):
        """ return ordered list of schemata names """
        return [n for n in self.Schema().getSchemataNames() if not n in ('default', 'metadata')]

    def base_edit(self, RESPONSE):
        """ redirect to our own edit method """
        RESPONSE.redirect('pcng_base_edit')

InitializeClass(Base)


class ParentManagedSchema:
    """ mix-in class for AT content-types whose schema is managed by
        the parent container and retrieved through acquisition.
    """
    
    def Schemata(self):
        """ return dict of Schematas """

        d = {}
        schema = self.Schema()
        for name in schema.getSchemataNames():
            s = Schema()
            for f in schema.getSchemataFields(name):
                s.addField(f)
            d[name] = s
        return d


    def Schema(self):
        """ Return our schema (through acquisition....uuuuuh). We override
            the Archetypes implementation because the schema for Issue is 
            maintained as attribute of the parent collector instance.
        """
        
        # Schema seems to be called during the construction phase when there is
        # not acquisition context. So we return the schema itself.

        if not hasattr(self, 'aq_parent'): return self.schema

        # Otherwise get the schema from the parent collector through
        # acquisition and assign it to a volatile attribute for performance
        # reasons

        schema = getattr(self, '_v_schema', None)
        if schema is None:
            self._v_schema = self.aq_parent.atse_getSchema()

            # Check if we need to update our own properties
            for field in self._v_schema.fields():
                try:
                    value = field.storage.get(field.getName(), self)  
                except:
                    field.storage.set(field.getName(), self, field.default)
                
        return self._v_schema

InitializeClass(ParentManagedSchema)