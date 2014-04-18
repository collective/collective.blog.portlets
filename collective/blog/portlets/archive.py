from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import monthname_msgid
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.blog.portlets import _
from collective.blog.portlets.utils import find_assignment_context
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.interface import implements


class IArchivePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(title=_(u'Title of the portlet'),
                             description=_(u'The text that will be shown as the title of the portlet'),
                             required=False)

    archive_view = schema.TextLine(title=_(u"Archive view"),
                                   description=_(u"The name of the archive view"),
                                   default=u'blog_view',
                                   required=True)


    reversed = schema.Bool(title=_(u"Reverse year and month list"),
                           description=_(u"When checked, the first shown year will be the current one, and then the previous ones. The same applies to the months"),
                           default=False,
                           )


    depth = schema.Int(title=_(u"Sub-folder depth"),
                       description=_(u"To include blog posts in subfolders, set this to the depth of the subfolders. 0 means no subfolders"),
                       default=0,
                       min=0,
                       # Setting this to 1000000 or similar will slow down the site,
                       # so let's prevent silly values.
                       max=100, 
                       )


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IArchivePortlet)

    header = u'Monthly archive'
    archive_view = u'blog_view'
    reversed = False
    depth = 0

    def __init__(self, header=u'Monthly archive',
                       archive_view=u'blog_view',
                       reversed=False,
                       depth=0):

        self.header = header
        self.archive_view = archive_view
        self.reversed = reversed

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _("Monthly archive")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('archive.pt')

    def update(self):
        self._counts = {}
        catalog = getToolByName(self.context, 'portal_catalog')
        # Get the path of where the portlet is created. That's the blog.
        assignment_context = find_assignment_context(self.data, self.context)
        if assignment_context is None:
            assignment_context = self.context
        self.folder_path = '/'.join(assignment_context.getPhysicalPath())
        self.folder_url = assignment_context.absolute_url()

        # Find the blog types:
        portal_properties = getToolByName(self.context, 'portal_properties', None)
        site_properties = getattr(portal_properties, 'site_properties', None)
        portal_types = site_properties.getProperty('blog_types', None)
        if portal_types == None:
            portal_types = ('Document', 'News Item', 'File')

        # Because of ExtendedPathIndex being braindead it's tricky (read:
        # impossible) to get all subobjects for all folders, without also
        # getting the folder. So we set a specific depth.
        brains = catalog(path={'query': self.folder_path, 'depth': self.data.depth + 1},
                         portal_type=portal_types)
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
        items = sorted(self._counts.keys())
        if self.data.reversed:
            return reversed(items)

        return items

    def months(self, year):
        # sort as integers, return as strings
        _months = sorted([int(m) for m in self._counts[year].keys()])
        items = [str(m) for m in _months]
        if self.data.reversed:
            return reversed(items)

        return items

    def monthname(self, month):
        return monthname_msgid(month)

    def count(self, year, month):
        return self._counts[year][month]

    def archive_url(self, year, month):
        return '%s/%s?year=%s&month=%s' % (self.folder_url,
                                           self.data.archive_view,
                                           year, month)


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IArchivePortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IArchivePortlet)
