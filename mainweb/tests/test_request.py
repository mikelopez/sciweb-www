"""
Tests the request process and how we will 
find the site and website pages related.

- When a request comes in, we search for the Website object.
- If there is no path in the url, return Index Page.
- If there is path in the URL, check if static, static-arg, or 
"""

from basetests import *
from mainweb.models import Website, WebsitePage

class TestRequests(BaseTestCase):
    """
    Tests the request process when an http request comes in.
    """
    def setUp(self):
        pass

    def test_get_website(self):
        """
        Simulate a request and get the website.
        The request must contain HTTP_HOST key with
        a value of a full URL like:
        http://www.sitename.com/whatever/else
        """
        request = {'HTTP_HOST': 'http://www.site.com/'}
        website = Website.objects.get_from_request(request)
        self.assertEquals(website, None)
        # add the site
        w = self.create_website(domain='site.com')
        website = Website.objects.get_from_request(request)
        self.assertTrue(website)
        self.assertEquals(getattr(website, 'domain', 'x'), 'site.com')
