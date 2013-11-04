from basetests import *


class MainwebTestCase(BaseTestCase):
    """
    Tests the mainweb app.
    Tests adding websites, websitepages & checking for sitepage rules.
    """
    tables = [Website, WebsitePage, ShopCategory]
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
        self.assertEquals(getattr(wp, 'type'), "index")

    def test_sitepage_name_in_staticpages(self):
        """When the name of the sitepage is the name
        of a staticpage, it will set the type to static."""
        wp = WebsitePage(website=self.create_website(),
                        title="My site", name="products",
                        template="index.html")
        wp.save()
        self.assertEquals(getattr(wp, 'type'), "static")
        
    def test_sitepage_name_in_staticargpages(self):
        """When the name of the sitepage is the name
        of a static-arg-page, it will set the type to 
        static-arg."""
        wp = WebsitePage(website=self.create_website(),
                        title="My site", name="search",
                        template="index.html")
        wp.save()
        self.assertEquals(getattr(wp, 'type'), "static-arg")

    def test_sitepage_default_type(self):
        """Tests the default type for a sitepage given the 
        type is not selected."""
        wp = WebsitePage(website=self.create_website(),
                        title="My site", name="Somepage",
                        template="index.html")
        wp.save()
        self.assertEquals(getattr(wp, 'type'), "sub-landing")

 
    def test_website_domain_fix(self):
        """Strips out any special characters from the url leaving
        it as domainname.com from http://www.domainname.com
        """
        w = Website(domain="http://www.somewebsite.com")
        w.save()
        self.assertEquals(getattr(w, 'domain'), 'somewebsite.com')

    def test_pagetypes(self):
        """Checks for the right page types for WebsitePage. """
        pass
