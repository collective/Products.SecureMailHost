# 
#
# Generated by dumpDCWorkflow.py written by Sebastien Bigaret
# Original workflow id/title: psc_package_workflow/PSC Package workflow
# Date: 2005/02/03 00:53:29.268 GMT
#
# WARNING: this dumps does NOT contain any scripts you might have added to
# the workflow, IT IS YOUR RESPONSABILITY TO MAKE BACKUPS FOR THESE SCRIPTS.
#
# No script detected in this workflow
# 
"""
Programmatically creates a workflow type
"""
__version__ = "$Revision: 1.2 $"[11:-2]

from Products.CMFCore.WorkflowTool import addWorkflowFactory

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

def setupPSC_package_workflow(wf):
    "..."
    wf.setProperties(title='PSC Package workflow')

    for s in ['pending', 'unapproved', 'published']:
        wf.states.addState(s)
    for t in ['retract', 'submit', 'publish', 'reject']:
        wf.transitions.addTransition(t)
    for v in ['action', 'review_history', 'actor', 'comments', 'time']:
        wf.variables.addVariable(v)
    for l in ['reviewer_queue']:
        wf.worklists.addWorklist(l)
    for p in ('Access contents information', 'Modify portal content', 'View', 'Add portal content', 'Add PloneSoftwareCenter Content'):
        wf.addManagedPermission(p)
        

    ## Initial State
    wf.states.setInitialState('unapproved')

    ## States initialization
    sdef = wf.states['pending']
    sdef.setProperties(title="""Waiting for reviewer""",
                       transitions=('publish', 'reject', 'retract'))
    sdef.setPermission('Access contents information', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('Modify portal content', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('View', 0, ['Manager', 'Owner', 'Reviewer'])
    sdef.setPermission('Add PloneSoftwareCenter Content', 0, ['Manager', 'Owner', 'Reviewer'])

    sdef = wf.states['unapproved']
    sdef.setProperties(title="""Unapproved package, awaiting release""",
                       transitions=('publish', 'submit'))
    sdef.setPermission('Access contents information', 0, ['Manager', 'Owner'])
    sdef.setPermission('Modify portal content', 0, ['Manager', 'Owner'])
    sdef.setPermission('View', 0, ['Manager', 'Owner'])
    sdef.setPermission('Add PloneSoftwareCenter Content', 0, ['Manager', 'Owner'])

    sdef = wf.states['published']
    sdef.setProperties(title="""Public""",
                       transitions=('reject', 'retract'))
    sdef.setPermission('Access contents information', 1, ['Anonymous', 'Manager', 'Member', 'Owner'])
    sdef.setPermission('Modify portal content', 0, ['Manager', 'Owner'])
    sdef.setPermission('View', 1, ['Anonymous', 'Manager', 'Member', 'Owner'])
    sdef.setPermission('Add PloneSoftwareCenter Content', 0, ['Manager', 'Owner'])


    ## Transitions initialization
    tdef = wf.transitions['retract']
    tdef.setProperties(title="""Member retracts submission""",
                       new_state_id="""new""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Retract""",
                       actbox_url="""%(content_url)s/content_retract_form""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'Request review'},
                       )

    tdef = wf.transitions['submit']
    tdef.setProperties(title="""Member requests publishing""",
                       new_state_id="""pending""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Submit""",
                       actbox_url="""%(content_url)s/content_submit_form""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'Request review'},
                       )

    tdef = wf.transitions['publish']
    tdef.setProperties(title="""Reviewer publishes content""",
                       new_state_id="""published""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Publish""",
                       actbox_url="""%(content_url)s/content_publish_form""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'Review portal content'},
                       )

    tdef = wf.transitions['reject']
    tdef.setProperties(title="""Reviewer rejects submission""",
                       new_state_id="""new""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Reject""",
                       actbox_url="""%(content_url)s/content_reject_form""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'Review portal content'},
                       )

    ## State Variable
    wf.variables.setStateVar('review_state')

    ## Variables initialization
    vdef = wf.variables['action']
    vdef.setProperties(description="""The last transition""",
                       default_value="""""",
                       default_expr="""transition/getId|nothing""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['review_history']
    vdef.setProperties(description="""Provides access to workflow history""",
                       default_value="""""",
                       default_expr="""state_change/getHistory""",
                       for_catalog=0,
                       for_status=0,
                       update_always=0,
                       props={'guard_permissions': 'Request review; Review portal content'})

    vdef = wf.variables['actor']
    vdef.setProperties(description="""The ID of the user who performed the last transition""",
                       default_value="""""",
                       default_expr="""user/getId""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['comments']
    vdef.setProperties(description="""Comments about the last transition""",
                       default_value="""""",
                       default_expr="""python:state_change.kwargs.get('comment', '')""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['time']
    vdef.setProperties(description="""Time of the last transition""",
                       default_value="""""",
                       default_expr="""state_change/getDateTime""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    ## Worklists Initialization
    ldef = wf.worklists['reviewer_queue']
    ldef.setProperties(description="""Reviewer tasks""",
                       actbox_name="""Pending (%(count)d)""",
                       actbox_url="""%(portal_url)s/search?review_state=pending""",
                       actbox_category="""global""",
                       props={'guard_permissions': 'Review portal content', 'var_match_review_state': 'pending'})


def createPSC_package_workflow(id):
    "..."
    ob = DCWorkflowDefinition(id)
    setupPSC_package_workflow(ob)
    return ob

def install ():
    addWorkflowFactory(createPSC_package_workflow,
                       id='psc_package_workflow',
                       title='PSC Package workflow')

    
