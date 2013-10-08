from basetests import *
from mainweb.models import Website, WebsitePage


class TestModelWebsite(TestCase):
    """
    Test the basic model classes
    Should have the following:
     - Website
     - WebsitePage
    """
    tables = [Website, WebsitePage]
    table_struct = []

    default_website = None
    def setUp(self):
        pass

    def test_create_website(self):
        """Creates a website."""
        website = self.create_website()
        self.assertTrue(website)
        return website

    def test_create_websitepage(self):
        """Creates a sitepage."""
        self.assertTrue(WebsitePage.PAGETYPES)
        wp = WebsitePage(website=self.create_website(),
                         title="MySite", name="MySite",
                         type="index", template="index.html",
                         redirects_to=None)
        wp.save()
        self.assertTrue(wp)

    def test_sitepage_index_name(self):
        """When providing 'index' as sitepage name, it will
        set the type to index automatically."""
        wp = WebsitePage(website=self.create_website(),
                        title="My site", name="index",
                        template="index.html")
        wp.save()
        self.assertEquals(wp.type, 'index')

    def test_sitepage_name_in_staticpages(self):
        """When the name of the sitepage is the name
        of a staticpage, it will set the type to static."""
        wp = WebsitePage(website=self.create_website(),
                        title="My site", name="products",
                        template="index.html")
        wp.save()
        self.assertEquals(wp.type, "static")
        









        



