#
# Generated by dumpDCWorkflow.py written by Sebastien Bigaret
# Original workflow id/title: pcng_issue_workflow/Workflow for PloneCollectorNG issues
# Date: 2004/03/01 19:28:12.032 GMT+1
#
# WARNING: this dumps does NOT contain any scripts you might have added to
# the workflow, IT IS YOUR RESPONSABILITY TO MAKE BACKUPS FOR THESE SCRIPTS.
#
# The following scripts have been detected and should be backed up:
# - send_notifications (Script (Python))
# - addAssignees (Script (Python))
# 
"""
Programmatically creates a workflow type
"""
__version__ = "$Revision: 1.8 $"[11:-2]

from Products.CMFCore.WorkflowTool import addWorkflowFactory

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

# NOTE: id + title must be added manually  
id = 'pcng_issue_workflow'
title = 'PloneCollectorNG default workflow'

def setupPcng_issue_workflow(wf):
    "..."
    wf.setProperties(title='Workflow for PloneCollectorNG issues')

    for s in ['resolved', 'resigned', 'created', 'rejected', 'defered', 'accepted', 'pending', 'wont_fix']:
        wf.states.addState(s)
    for t in ['defer', 'resolve', 'reject', 'resign', 'accept', 'reaccept', 'assign', 'pending', 'wont_fix']:
        wf.transitions.addTransition(t)
    for v in ['confidential', 'assigned_to']:
        wf.variables.addVariable(v)
    for l in []:
        wf.worklists.addWorklist(l)
    for p in ():
        wf.addManagedPermission(p)
        

    ## Initial State
    wf.states.setInitialState('created')

    ## States initialization
    sdef = wf.states['resolved']
    sdef.setProperties(title="""""",
                       transitions=('reaccept',))
    
    sdef = wf.states['wont_fix']
    sdef.setProperties(title="""""",
                       transitions=('reaccept',))

    sdef = wf.states['resigned']
    sdef.setProperties(title="""resign issue...no idea what to do with the issue""",
                       transitions=('reaccept',))

    sdef = wf.states['created']
    sdef.setProperties(title="""""",
                       transitions=('pending',))

    sdef = wf.states['rejected']
    sdef.setProperties(title="""""",
                       transitions=('reaccept',))

    sdef = wf.states['defered']
    sdef.setProperties(title="""issue effort delayed """,
                       transitions=('reaccept',))

    sdef = wf.states['accepted']
    sdef.setProperties(title="""""",
                       transitions=('assign', 'defer', 'reject', 'resign', 'resolve', 'wont_fix'))

    sdef = wf.states['pending']
    sdef.setProperties(title="""""",
                       transitions=('accept', 'defer', 'reject', 'resign', 'resolve', 'wont_fix'))


    ## Transitions initialization
    tdef = wf.transitions['defer']
    tdef.setProperties(title="""defer an issue""",
                       new_state_id="""defered""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""send_notifications""",
                       actbox_name="""defer""",
                       actbox_url="""""",
                       actbox_category="""pcng_issue_workflow""",
                       props={'guard_roles': 'TrackerAdmin; Supporter; Owner'},
                       )
    tdef.addVariable(id='assigned_to', text="python: list(state_change.kwargs['assignees'])")

    tdef = wf.transitions['resolve']
    tdef.setProperties(title="""Mark issue as resolved""",
                       new_state_id="""resolved""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""send_notifications""",
                       actbox_name="""resolve""",
                       actbox_url="""""",
                       actbox_category="""pcng_issue_workflow""",
                       props={'guard_roles': 'TrackerAdmin; Supporter; Owner'},
                       )
    tdef.addVariable(id='assigned_to', text="python: list(state_change.kwargs['assignees'])")

    tdef = wf.transitions['wont_fix']
    tdef.setProperties(title="""Issue will not be fixed""",
                       new_state_id="""wont_fix""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""send_notifications""",
                       actbox_name="""wont_fix""",
                       actbox_url="""""",
                       actbox_category="""pcng_issue_workflow""",
                       props={'guard_roles': 'TrackerAdmin; Supporter; Owner'},
                       )
    tdef.addVariable(id='assigned_to', text="python: list(state_change.kwargs['assignees'])")

    tdef = wf.transitions['reject']
    tdef.setProperties(title="""Reject the issue""",
                       new_state_id="""rejected""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""send_notifications""",
                       actbox_name="""reject""",
                       actbox_url="""""",
                       actbox_category="""pcng_issue_workflow""",
                       props={'guard_roles': 'TrackerAdmin; Supporter; Owner'},
                       )
    tdef.addVariable(id='assigned_to', text="python: list(state_change.kwargs['assignees'])")

    tdef = wf.transitions['resign']
    tdef.setProperties(title="""resign""",
                       new_state_id="""resigned""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""send_notifications""",
                       actbox_name="""resign""",
                       actbox_url="""""",
                       actbox_category="""pcng_issue_workflow""",
                       props={'guard_roles': 'TrackerAdmin; Supporter; Owner'},
                       )
    tdef.addVariable(id='assigned_to', text="python: list(state_change.kwargs['assignees'])")

    tdef = wf.transitions['accept']
    tdef.setProperties(title="""Accept issue and assign supporters""",
                       new_state_id="""accepted""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""send_notifications""",
                       actbox_name="""accept""",
                       actbox_url="""""",
                       actbox_category="""pcng_issue_workflow""",
                       props={'guard_roles': 'TrackerAdmin; Supporter; Reporter'},
                       )
    tdef.addVariable(id='assigned_to', text="python: list(state_change.kwargs['assignees'])")

    tdef = wf.transitions['reaccept']
    tdef.setProperties(title="""Re-Accept an issue when the issue has been in a final state""",
                       new_state_id="""accepted""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""send_notifications""",
                       actbox_name="""reaccept""",
                       actbox_url="""""",
                       actbox_category="""pcng_issue_workflow""",
                       props={'guard_roles': 'TrackerAdmin; Supporter'},
                       )

    tdef = wf.transitions['assign']
    tdef.setProperties(title="""reassign """,
                       new_state_id="""""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""send_notifications""",
                       actbox_name="""assign""",
                       actbox_url="""""",
                       actbox_category="""pcng_issue_workflow""",
                       props={'guard_roles': 'TrackerAdmin; Supporter'},
                       )
    tdef.addVariable(id='assigned_to', text="python: state_change.kwargs['assignees']")

    tdef = wf.transitions['pending']
    tdef.setProperties(title="""""",
                       new_state_id="""pending""",
                       trigger_type=0,
                       script_name="""send_notifications""",
                       after_script_name="""""",
                       actbox_name="""pending""",
                       actbox_url="""""",
                       actbox_category="""pcng_issue_workflow""",
                       props=None,
                       )
    tdef.addVariable(id='confidential', text='python: 0')

    ## State Variable
    wf.variables.setStateVar('state')

    ## Variables initialization
    vdef = wf.variables['confidential']
    vdef.setProperties(description="""""",
                       default_value="""""",
                       default_expr="""""",
                       for_catalog=1,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['assigned_to']
    vdef.setProperties(description="""""",
                       default_value="""""",
                       default_expr="""""",
                       for_catalog=1,
                       for_status=1,
                       update_always=1,
                       props=None)

    ## Worklists Initialization

def createPcng_issue_workflow(id):
    "..."
    ob = DCWorkflowDefinition(id)
    setupPcng_issue_workflow(ob)
    return ob

addWorkflowFactory(createPcng_issue_workflow,
                   id=id,
                   title=title)


