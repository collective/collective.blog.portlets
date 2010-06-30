Introduction
============

This product contains a set of portlets aimed at blogging, but useable also
for other situtations.

It supports Plone 3 and Plone 4.


The development of collective.blog.portlets was sponsored by the 
**Bergen Public Library** - http://www.nettbiblioteket.no


Portlets
--------

The portlets so far is:

* Monthly archive portlet: A portlet that shows a monthly archive view of all 
  content in a folder with number of items per month and a customizable link
  to an archive view.
  
* Last posts portlet: Lists the last X documents (sorted by effective date).

Installation is done in the usual manner: Add collective.blog.portlets to your
buildout, and install through QuickInstaller or portal_setup. You can
then add portlets in the usual manner.

Settings
--------

collective.blog.view has only one settings, locate in
``portal_properties.site_properties``.

* **blog_types**: This lines property will be used to contain the portal_types
  that are considered entries in the blog. If it does not exist, it will 
  default to `Document`, `News Item` and `File`.

This product will never use doctests to test anything besides documentation.


