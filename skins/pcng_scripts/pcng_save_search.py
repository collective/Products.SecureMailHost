##parameters=query,query_id

# Save a query as memberdata preference 'pcng_saved_searches' which
# itself is a list of queries in the form 
# 'RELATIVE_URL_OF_COLLECTOR:query_id::QUERY_STRING'

mstool = context.portal_membership

if mstool.isAnonymousUser(): 
    msg = context.Translate('unknown_user', 'Unknown user')
    context.REQUEST.RESPONSE.redirect('pcng_view?portal_status_message=%s' % msg)
    return

member = mstool.getAuthenticatedMember()
saved_searches = member.getProperty('pcng_saved_searches', [])
if saved_searches is (): saved_searches = []

for search in saved_searches:
    if search.startswith(query_id + '::'):
        raise ValueError(context.Translate('id_already_in_use', 'ID already in use: $id', id=query_id))

saved_searches.append('%s::%s::%s' % (context.absolute_url(1), query_id, query))
member.setProperties({'pcng_saved_searches' : saved_searches})


msg = context.Translate('search_saved', 'Search saved')
context.REQUEST.RESPONSE.redirect('pcng_view?portal_status_message=%s' % msg)
