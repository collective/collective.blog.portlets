from zope.component import getUtility, getMultiAdapter, ComponentLookupError
from plone.portlets.interfaces import IPortletAssignmentMapping, IPortletManager

def find_assignment_context(assignment, context):
    # Finds the creation context of the assignment
    context = context.aq_inner
    manager_name = assignment.manager.__name__
    assignment_name = assignment.__name__
    while True:
        try:
            manager = getUtility(IPortletManager, manager_name, context=context)
            mapping = getMultiAdapter((context, manager), IPortletAssignmentMapping)
            if assignment_name in mapping:
                if mapping[assignment_name] is assignment.aq_base:
                    return context
        except ComponentLookupError:
            pass
        parent = context.aq_parent
        if parent is context:
            return None
        context = parent
