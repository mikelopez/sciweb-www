import logging

from os import path
from django.test import TestCase
from django.conf import settings
from nose.tools import assert_true, assert_equals, assert_false
from django.core.exceptions import ValidationError

from mainweb.models import Website, WebsitePage,\
                          STATIC_PAGES, STATIC_ARG_PAGES


debug_filename = getattr(settings, 'SHOPZILLA_OUTPUT_FILE', '')

class BaseTestCase(TestCase):
    """ Base Test Class for Main Web Functions """

    def setUp(self):
        """ Check the settings """
        pass
        
    def tearDown(self):
        pass

    def create_website(self, **kwargs):
        """Creates a website."""
        if not kwargs:
            kwargs = {'name': "domain%s.com" % randint(111,9999)}
        w = Website(**kwargs)
        w.save()
        return w

    def create_websitepage(self, **kwargs):
        """Creates a website page."""
        if not kwargs:
            kwargs = {'name': "domain%s.com" % randint(111,9999)}
        w = WebsitePage(**kwargs)
        w.save()
        return w
