# 
#
# Generated by dumpDCWorkflow.py written by Sebastien Bigaret
# Original workflow id/title: psc_area_workflow/PSC Area workflow
# Date: 2005/02/03 00:52:02.054 GMT
#
# WARNING: this dumps does NOT contain any scripts you might have added to
# the workflow, IT IS YOUR RESPONSABILITY TO MAKE BACKUPS FOR THESE SCRIPTS.
#
# No script detected in this workflow
# 
"""
Programmatically creates a workflow type
"""
__version__ = "$Revision: 1.5 $"[11:-2]

from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

from Products.CMFCore import CMFCorePermissions

ACCESS = CMFCorePermissions.AccessContentsInformation
VIEW   = CMFCorePermissions.View
MODIFY = CMFCorePermissions.ModifyPortalContent
ADD    = CMFCorePermissions.AddPortalContent

def setupPSC_area_workflow(wf):
    "..."
    wf.setProperties(title='PSC Area workflow')

    for s in ['closed', 'published']:
        wf.states.addState(s)
    for t in ['retract', 'publish']:
        wf.transitions.addTransition(t)
    for v in ['action', 'review_history', 'actor', 'comments', 'time']:
        wf.variables.addVariable(v)
    for l in ['reviewer_queue']:
        wf.worklists.addWorklist(l)
    for p in (ACCESS, VIEW, MODIFY, ADD):
        wf.addManagedPermission(p)
        

    ## Initial State
    wf.states.setInitialState('closed')

    ## States initialization
    sdef = wf.states['closed']
    sdef.setProperties(title="""Closed to the public""",
                       transitions=('publish',))
    sdef.setPermission(ACCESS, 1, ['Member','Manager', 'Owner'])
    sdef.setPermission(VIEW, 1, ['Member', 'Manager', 'Owner'])
    sdef.setPermission(MODIFY, 0, ['Manager', 'Owner'])
    sdef.setPermission(ADD, 1, ['Manager','Owner'])

    sdef = wf.states['published']
    sdef.setProperties(title="""Open for submissions""",
                       transitions=('retract',))
    sdef.setPermission(ACCESS, 1, ['Anonymous', 'Member', 'Manager', 'Owner'])
    sdef.setPermission(VIEW, 1, ['Anonymous', 'Member', 'Manager', 'Owner'])
    sdef.setPermission(MODIFY, 0, ['Manager', 'Owner'])
    sdef.setPermission(ADD, 1, ['Member', 'Manager', 'Owner'])


    ## Transitions initialization
    tdef = wf.transitions['retract']
    tdef.setProperties(title="""Close area""",
                       new_state_id="""closed""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Retract""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': MODIFY},
                       )

    tdef = wf.transitions['publish']
    tdef.setProperties(title="""Open area to submissions""",
                       new_state_id="""published""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Publish""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': MODIFY},
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


def createPSC_area_workflow(id):
    "..."
    ob = DCWorkflowDefinition(id)
    setupPSC_area_workflow(ob)
    return ob

def install ():
    addWorkflowFactory(createPSC_area_workflow,
                       id='psc_area_workflow',
                       title='PSC Area workflow')

    
