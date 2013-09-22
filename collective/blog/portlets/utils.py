from Acquisition import aq_inner, aq_parent, aq_base
from plone.portlets.interfaces import IPortletAssignmentMapping, IPortletManager
from zope.component import getUtility, getMultiAdapter, ComponentLookupError


def find_assignment_context(assignment, context):
    # Finds the creation context of the assignment
    context = aq_inner(context)
    manager_name = assignment.manager.__name__
    assignment_name = assignment.__name__
    while True:
        try:
            manager = getUtility(IPortletManager, manager_name, context=context)
            mapping = getMultiAdapter((context, manager), IPortletAssignmentMapping)
            if assignment_name in mapping:
                if aq_base(mapping[assignment_name]) is aq_base(assignment):
                    return context
        except ComponentLookupError:
            pass
        parent = aq_parent(context)
        if parent is context:
            return None
        context = parent
