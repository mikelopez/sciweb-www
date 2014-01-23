import simplejson
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpRequest, Http404, HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse, resolve
from django.template import RequestContext, loader, Context
from datetime import datetime

from mainweb.models import Website, WebsitePage, RecentSearches, RecentProducts, \
                            ProductLinks, Provider, MainCategory
#from products.models import Product
#from lib.mainlogger import LoggerLog
from utils import get_meta_domain, shopzilla_search, shopzilla_compare
import logging
import os

from django.conf import settings
STATIC_PAGES = getattr(settings, 'STATIC_PAGES', None)
PROJECT_ROOTDIR = getattr(settings, 'PROJECT_ROOTDIR', None)
STATIC_ARG_PAGES = getattr(settings, 'STATIC_ARG_PAGES', None)
TEMPLATE_PATH = getattr(settings, 'TEMPLATE_PATH', None)
STATIC_URL = getattr(settings, 'STATIC_URL', None)
SHOPZILLA_TOKEN = getattr(settings, 'SHOPZILLA_TOKEN', None)
SHOPZILLA_PUB_TOKEN = getattr(settings, 'SHOPZILLA_PUB_TOKEN', None)
SHOPZILLA_OUTPUT_FILE = getattr(settings, 'SHOPZILLA_OUTPUT_FILE', None)
SHOPZILLA_SEARCH_FREQUENCY = getattr(settings, 'SHOPZILLA_SEARCH_FREQUENCY', None)
SHOP_SEARCH = getattr(settings, 'SHOP_SEARCH', None)
SHOP_COMPARE = getattr(settings, 'SHOP_COMPARE', None)

try:
    from settings import LOG_ON
except ImportError:
    LOG_ON = False

class PageProcessorException(Exception):
    """ Handle basic exceptions for PageProcessor """
    def __init__(self, message):
        Exception.__init__(self, message)

class TemplateFinder(object):
    """
    Find the template for a given domain 
    """
    domain = None
    def __init__(self, domain):
        self.domain = domain

    def find_template(self):
        """
        find the template
        """
        pass

class PageProcessor(object):
    """ 
    Process the page - check for any static urls or website PageProcessor
    URL-format http://sitename.com/linkname/filtername 
    """
    linkname = None
    filtername = None
    template = None
    request = None
    website = None
    websitepage = None
    domain = None
    pagetype = None

    default_static_dir = None
    static_dir = None

    default_template_dir = None
    template_dir = None

    shopzilla_products = None
    shopzilla_categories = []
    shopzilla_subcategories = []

    def __init__(self, request, linkname, filtername):
        """
        Process the request, if request not found, page processor exception is raised
        """
        self.linkname = linkname
        self.filtername = filtername
        self.request = request
        if not request:
            raise PageProcessorException('An error occured, not a valid request')
        self.process_page()

    def context(self):
        """
        Return the context based on class attrs 
        """
        # define the structure here - 
        data = {
            'linkname': None,
            'filtername': None,
            'template': None,
            'request': None,
            'website': None,
            'websitepage': None,
            'domain': None,
            'pagetype': None,
            'shopzilla_products': None,
            'shopzilla_categories': None,
            'shopzilla_subcategories': None,
            'product': None,
            'products': None,
            'categories': None,
            'category': None,
            'page_obj': None
        }
        for k, v in data.items():
            try:
                data[k] = getattr(self, k)
            except AttributeError:
                data[k] = None
        return data

    def process_page(self):
        """ 
        Here we will examine the URL and determine if it is a static
        URL, or if it is a WebsitePage
        if it is an index page, self.linkname is set to index
        get the website page, and process the page type which calls the predefined methods
        and sets the return data as needed 
        """
        # parse and get the domain
        self.domain = self.get_domain()
        if not self.domain:
            raise PageProcessorException('Domain returned None')
        self.website = self.get_website()

        # check if index page or not, set to index if linkname is None
        self.set_index()
        # get the sitepage, if its index, the index site page should exist
        page = self.get_websitepage()
        self.pagetype = page.type
        self.template = page.template

        # add additional stuff to the context
        self.process_pagename()

    def process_pagename(self):
        """
        Process and call the predefined method 
        for a specific page type
        static-arg will need to have filtername set
        """
        SSFQ = SHOPZILLA_SEARCH_FREQUENCY
        RS = RecentSearches
        pagenames = [SHOP_SEARCH, SHOP_COMPARE, 'product']

        if self.linkname == SHOP_SEARCH:
            searchfor = self.filtername
            rs = RS.objects.check_search(search=searchfor, network='shopzilla')
            if not rs:
                self.shopzilla_products, \
                self.shopzilla_subcategories = \
                        shopzilla_search(SHOPZILLA_PUB_TOKEN, 
                                         SHOPZILLA_TOKEN, 
                                         self.filtername,
                                         debug=True, 
                                         debug_filename=SHOPZILLA_OUTPUT_FILE)
                rs = RS.objects.record_search(search=searchfor,
                          network='shopzilla',
                          ip=self.request.META.get('REMOTE_ADDR'),
                          response_data=simplejson.dumps(self.shopzilla_products))
                rs.save()
            else:
                # dont query the API, load from the database ;)
                self.shopzilla_products = simplejson.loads(rs.response_data)

        if self.linkname == SHOP_COMPARE:
            searchfor = self.filtername
            RP = RecentProducts
            rp = RP.objects.check_search(product_id=searchfor, network='shopzilla')
            if not rp:
                self.shopzilla_products, \
                self.shopzilla_subcategories = \
                        shopzilla_compare(SHOPZILLA_PUB_TOKEN, 
                                          SHOPZILLA_TOKEN, 
                                          self.filtername, 
                                          debug=True, 
                                          debug_filename=SHOPZILLA_OUTPUT_FILE)
                rp = RP.objects.record_search(product_id=searchfor,
                          network='shopzilla',
                          ip=self.request.META.get('REMOTE_ADDR'),
                          response_data=simplejson.dumps(self.shopzilla_products))
                rp.save()
            else:
                self.shopzilla_products = simplejson.loads(rp.response_data)

        if self.linkname == 'product':
            # get the product
            self.get_product()

        # any other page (including index)
        if not self.linkname in pagenames:
            self.fetch_page()


    def set_index(self):
        """
        This will get the index page if no linkname is found.
        """
        if not self.linkname:
            self.linkname = 'index'


    def get_website(self, force=True):
        """
        Get the website
        if self.website is not set, it will set it
        if force is set, it will override self.website
        otherwise return self.website if set
        """
        if self.websitepage:
            if not force:
                return self.website
        # setting or overriding
        try:
            self.website = Website.objects.get(domain=self.get_domain())
        except Website.MultipleObjectsReturned:
            # catch multi's and log it
            self.website = Website.objects.filter(domain=self.get_domain())[0]
        except Website.DoesNotExist:
            raise PageProcessorException('No website for %s' % self.get_domain())
        return self.website


    def get_websitepage(self, force=True):
        """
        Get the website page
        if website page is set, return self.WebsitePage
        if force is true, and website page is set, override it
        if no linkname is found, index must be set by calling self.set_index()
        """
        if self.websitepage:
            if not force:
                return self.websitepage
        # setting or overriding
        try:
            self.websitepage = WebsitePage.objects.get(website=self.website, name=self.linkname)
        except WebsitePage.DoesNotExist:
            raise PageProcessorException('No website page for %s' % self.linkname)
        except WebsitePage.MultipleObjectsReturned:
            self.websitepage = WebsitePage.objects.filter(website=self.website, name=self.linkname)[0]
        return self.websitepage

    def fetch_page(self):
        """
        Fetches a pages data according to rules.
        """
        filters = {'active': True}
        redirect_to = self.websitepage.redirects_to
        show_productlinks = self.websitepage.show_productlinks
        filter_provider = self.websitepage.filter_provider
        filter_category = self.websitepage.filter_category
        if redirect_to:
            return HttpResponseRedirect(redirect_to)
        if show_productlinks:
            if filter_provider:
                filters['provider'] = filter_provider
            if filter_category:
                filters['category'] = filter_category
            pagenum = self.request.GET.get('page', int(1))
            pg = Paginator(ProductLinks.objects.filter(**filters), \
                           self.websitepage.paginate_by).page(pagenum)
            self.page_obj = pg
            self.products = self.page_obj.object_list


    def get_domain(self):
        """
        get the domain name from request
        """
        return get_meta_domain(self.request)

    def get_product(self):
        """
        Get a product 
        """
        # get the product
        pid = self.request.GET.get('p', self.filtername)
        self.product = ProductLinks.objects.getbypk(pid)
        # try by filter name
        if not getattr(self, 'product'):
            self.product = ProductLinks.objects.getbyfiltername(pid)


    def get_article(self, article=None):
        """
        Get article 
        """
        pass
        
    def search(self):
        """
        Search.
        """
        pass

    def get_template(self):
        """
        If template does is none, raise PageProcessor exception
        """
        template_filename = self.websitepage.template
        searchpath = '%s/domains/%s/%s' % (TEMPLATE_PATH, 
                                           self.website.domain, 
                                           template_filename)
        # if custom domain doesnt exist
        if os.path.exists(searchpath):
            #self.logger.write('Custom path domains exists, using that template!')
            return searchpath
        else:
            #self.logger.write('NOT FOUND default template %s' % (searchpath))
            raise PageProcessorException('No Page Found %s' % (searchpath))

        

    
        


        

