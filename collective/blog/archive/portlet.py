from zope.interface import implements
from zope.component import getUtility, getMultiAdapter, ComponentLookupError

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.CMFCore.utils import getToolByName
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager

from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

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

class IArchivePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IArchivePortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Archive Portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('portlet.pt')
    
    def update(self):
        self._counts = {}
        catalog = getToolByName(self.context, 'portal_catalog')
        # Get the path of where the portlet is created. That's the blog.
        assignment_context = find_assignment_context(self.data, self.context)
        path = '/'.join(assignment_context.getPhysicalPath())
        # Because of ExtendedPathIndex being braindead it's tricky (read:
        # impossible) to get all subobjects for all folder, without also
        # getting the folder. So we set depth to 1, which means we only get
        # the immediate children. This is not a bug, but a lack of feature.
        brains = catalog(path={'query': path, 'depth': 1})
        if not brains:
            return
        
        # Count the number of posts per month:
        allmonths = {}
        for brain in brains:
            effective = brain.effective
            year = str(effective.year())
            if year == '1000':
                continue # No effective date == not published
            month = str(effective.month())
            count = allmonths.setdefault((year, month), 0)
            allmonths[(year, month)] = count +1

        for year, month in allmonths:
            year = str(year)
            month = str(month)
            # Make sure there is a year in the _counts dict:
            self._counts.setdefault(year, {})
            # Add this month:
            months = self._counts[year]
            months[month] = allmonths[year, month]
            
    def years(self):
        return sorted(self._counts.keys())
    
    def months(self, year):
        return sorted(self._counts[year].keys())
    
    def count(self, year, month):
        return self._counts[year][month]

    
class AddForm(base.NullAddForm):
    """Portlet add form.
    """
    def create(self):
        return Assignment()
