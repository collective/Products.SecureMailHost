## Script (Python) "pcng_content_edit"
##title=Edit content
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=''

REQUEST = context.REQUEST

fieldset = REQUEST.get('fieldset', None)

if context.meta_type == 'PloneIssueNG':
   
    if context.isPersistent():
        # persistent issue 
        context.processForm()
        new_context = context
    else:
        # temporary issue 
        id = context.new_issue_number()
        parent = context.aq_parent.aq_parent  # tempissue -> tempfolder -> PCNG instance
        context.processForm()
        new_context = parent.move_temporary_issue(context, id)
        new_context.processForm()
        
else:
    new_context = context.portal_factory.doCreate(context, id)
    new_context.processForm()

# Assign ticket to assignees ('assign_ticket' is a hidden var
# set in pcng_base_edit.pt)

if REQUEST.get('assign_ticket', None) == '1':
    assignees = REQUEST.get('assignees', [])

    # added users from the assignes_group
    import group_assignment_policies
    groups = REQUEST.get('assignees_group', [])
    assignees.extend(group_assignment_policies.getUsersForGroups(context, groups))
    if assignees:
        new_context.issue_followup(action='accept', assignees=assignees)


portal_status_message = REQUEST.get('portal_status_message', new_context.Translate('changes_saved', 'Content changes saved'))
return state.set(status='success',
                 context=new_context,
                 fieldset=fieldset, 
                 portal_status_message=portal_status_message)

