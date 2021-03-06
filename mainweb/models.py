from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.conf import settings
from datetime import datetime, timedelta

SHOP_SEARCH = 'shopsearch'
SHOP_COMPARE = 'shopcompare'
SHOP_CATEGORY = 'shopcategory'

# static pages are pages that produce a list view with custom functionality
sp = ['products', 'articles']
# static arg pages would be a detail view of an object, but require a pk value 
sap = ['search', 'a', 'product', 
       SHOP_SEARCH, SHOP_COMPARE, SHOP_CATEGORY]

STATIC_PAGES = getattr(settings, "STATIC_PAGES", sp)
STATIC_ARG_PAGES = getattr(settings, "STATIC_ARG_PAGES", sap)
SHOPZILLA_SEARCH_FREQUENCY = getattr(settings, "SHOPZILLA_SEARCH_FREQUENCY", 30)

blankfield = {'blank': True, 'null': True}

class WebsiteManager(models.Manager):
    """Model manager for Website."""
    @classmethod
    def get_from_request(self, request):
        """Gets the website from request HTTP_HOST key"""
        try:
            sitename = request.get('HTTP_HOST')
        except AttributeError:
            sitename = None
        # if request.get returned None
        if not sitename:
            sitename = request.META.get('HTTP_HOST')
        
        domain = sitename.replace('http://', '').replace('www.', '').replace('/','')
        if not domain:
            return None

        # filter out any dev ports
        domain = domain.split(':')[0]
        try:
            ws = Website.objects.get(domain=domain)
        except Website.DoesNotExist:
            return None
        return ws


class Website(models.Model):
    """
    Creates a website 
    """
    domain = models.CharField(max_length=40)
    meta_desc = models.TextField(**blankfield)
    meta_key = models.TextField(**blankfield)
    notes = models.TextField(**blankfield)
    active = models.NullBooleanField(default=True)
    objects = WebsiteManager()
    
    def __str__(self):
        return str(self.domain)

    def __unicode__(self):
        return unicode(self.domain)

    @property 
    def has_pages(self):
        return self.websitepage_set.select_related()

    def get_absolute_url(self):
        return reverse('website_detail', kwargs={'pk': self.pk})

    def get_index_page(self):
        """ get the index page """
        try:
            return self.website_set.select_related().filter(name='index')[0]
        except:
            return None

    def save(self, *args, **kwargs):
        self.domain = self.domain.replace('http://', '').replace('/','').replace('www.','').split(':')[0]
        try:
            website = Website.objects.get(domain=self.domain)
            pass
        except Website.DoesNotExist:
            super(Website, self).save(*args, **kwargs)


class WebsitePage(models.Model):
    """ 
    Represents a webpage on a particular website
    Sets 'index' as default.
    Page Types:
      - Static Arg: This is a static page that requires a content_type and object_pk 
      - Static: Static pages are pages with a predefined method. E.g, products
          will search the products database and return products variable.
          You can introduce new static pages with predefined methods for custom apps
      - Sub-Landing: A custom subpage or landing page at the top level or url (sitename.com/subpage) - 
          this has to be a name that is not defined in as a "static" url. For example, a contact us page specific
          for the site you are making, or a landing page for marketing

    """
    PAGETYPES = (('sub-landing', 'sub-landing',), ('index', 'index'), \
        ('static', 'static',),('static-arg', 'static-arg',),)
    
    custom_blankfield = blankfield
    custom_blankfield['max_length']= 30

    website = models.ForeignKey('Website')
    title = models.CharField(max_length=50, default='')
    meta_desc = models.TextField(**blankfield)
    meta_key = models.TextField(**blankfield)
    name = models.CharField(max_length=20, default='index')
    type = models.CharField(max_length=15, choices=PAGETYPES, default='sub-landing')
    template = models.CharField(max_length=50, blank=True, null=True)
    redirects_to = models.CharField(**custom_blankfield)
    show_categories = models.NullBooleanField(blank=True, null=True, default=False)
    show_productlinks = models.NullBooleanField(blank=True, null=True, default=False)
    filter_category = models.ForeignKey('MainCategory', blank=True, null=True)
    filter_provider = models.ForeignKey('Provider', blank=True, null=True)
    paginate_by = models.IntegerField(blank=True, null=True, default=10)
    active = models.NullBooleanField(blank=True, null=True, default=False)
    class Meta:
        ordering = ('website',)

    def __str__(self):
        return str("%s / %s" % (self.website.domain, self.name))

    def __unicode__(self):
        return unicode("%s / %s" % (self.website.domain, self.name))

    def get_absolute_url(self):
        return reverse('websitepage_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """ 
        Parse the name and save 
        raise validation error if name is in static-pages or 
        static-arg-page list
        if name is index, set type to index

        """
        self.name = self.name.lower().replace(' ', '_').replace('.','').replace('/','')
        # override index as type if name matches
        if self.name == 'index':
            self.type = 'index'

        # override title if nothing is set
        if not self.title:
            self.title = self.name
            
        # just incase
        if not self.type:
            self.type = self.PAGETYPES[0][0]
        super(WebsitePage, self).save(*args, **kwargs)



class RecentSearchesManager(models.Manager):
    """Model manager for recent searches."""
    @classmethod
    def check_search(self, **kwargs):
        """Explicit is better than implicit"""
        if not kwargs:
            return None
        datesearch = datetime.now() - timedelta(seconds=60*SHOPZILLA_SEARCH_FREQUENCY)
        r = RecentSearches.objects.filter(placed__gt=datesearch,
                                          search=kwargs.get('search'),
                                          network=kwargs.get('network', 'shopzilla'))
        if r:
            try:
                return r[0]
            except:
                return None
        else:
            return None

    @classmethod
    def record_search(self, **kwargs):
        """Explicit is better than implicit"""
        if not kwargs:
            return None
        if not kwargs.get('ip'):
            return None
        r = RecentSearches(placed=datetime.now(),
                           search=kwargs.get('search'),
                           network=kwargs.get('network', 'shopzilla'),
                           ip=kwargs.get('ip'),
                           response_data=kwargs.get('response_data'))
        r.save()
        return r


class RecentSearches(models.Model):
    """Recent searches will be recorded and re-queried
    every 'x' minutes to avoid spammers and assholes."""
    search = models.CharField(max_length=50)
    placed = models.DateTimeField(default=datetime.now())
    network = models.CharField(max_length=50)
    ip = models.CharField(max_length=20)
    response_data = models.TextField(blank=True, null=True)
    objects = RecentSearchesManager()


class RecentProductsManager(models.Manager):
    """Model manager for recent searches."""
    @classmethod
    def check_search(self, **kwargs):
        """Explicit is better than implicit"""
        if not kwargs:
            return None
        # 24 hour requery
        datesearch = datetime.now() - timedelta(seconds=60*24)
        r = RecentProducts.objects.filter(placed__gt=datesearch,
                                          product_id=kwargs.get('product_id'),
                                          network=kwargs.get('network', 'shopzilla'))
        if r:
            try:
                return r[0]
            except:
                return None
        else:
            return None

    @classmethod
    def record_search(self, **kwargs):
        """Explicit is better than implicit"""
        if not kwargs:
            return None
        if not kwargs.get('ip'):
            return None
        r = RecentProducts(placed=datetime.now(),
                           product_id=kwargs.get('product_id'),
                           network=kwargs.get('network', 'shopzilla'),
                           ip=kwargs.get('ip'),
                           response_data=kwargs.get('response_data'))
        r.save()
        return r


class RecentProducts(models.Model):
    """Recent searches will be recorded and re-queried
    every 'x' minutes to avoid spammers and assholes."""
    product_id = models.CharField(max_length=50)
    placed = models.DateTimeField(default=datetime.now())
    network = models.CharField(max_length=50)
    ip = models.CharField(max_length=20)
    response_data = models.TextField(blank=True, null=True)
    objects = RecentProductsManager()


# Products and Links Models
class Provider(models.Model):
    """Provider class"""
    active = models.NullBooleanField(null=True, blank=True, default=False)
    name = models.CharField(max_length=100)
    filter_name = models.CharField(max_length=100, blank=True, null=True)
    login = models.CharField(max_length=50)
    website_registered = models.ForeignKey('Website')
    logo = models.TextField(blank=True, null=True)
    def __str__(self):
        return str(self.name)
    def __unicode__(self):
        return unicode(self.name)
    def get_absolute_url(self):
        return reverse('linkprovider_detail', kwargs={'pk': self.pk})
    def save(self):
        self.filter_name = self.name.replace(' ', '-')\
                                    .replace('.', '-')\
                                    .replace('&', '-and-')\
                                    .replace('$', '')\
                                    .replace("'", "")\
                                    .replace('"', '').lower()
        super(Provider, self).save()
    

class MainCategory(models.Model):
    active = models.NullBooleanField(null=True, blank=True, default=False)
    name = models.CharField(max_length=100)
    filter_name = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return str(self.name)
    def __unicode__(self):
        return unicode(self.name)
    def get_absolute_url(self):
        return reverse('maincategory_detail', kwargs={'pk': self.pk})
    def save(self):
        self.filter_name = self.name.replace(' ', '-')\
                                    .replace('.', '-')\
                                    .replace('&', '-and-')\
                                    .replace('$', '')\
                                    .replace("'", "")\
                                    .replace('"', '').lower()
        super(MainCategory, self).save()
    
class ProductLinksManager(models.Manager):
    @classmethod
    def getbypk(self, pk):
        try:
            return ProductLinks.objects.get(pk=pk)
        except (ValueError, ProductLinks.DoesNotExist):
            return None
        return None
    @classmethod
    def getbyfiltername(self, filtername):
        try:
            return ProductLinks.objects.get(filter_name=filtername)
        except (ValueError, ProductLinks.DoesNotExist):
            return None
        return None

class ProductLinks(models.Model):
    """Keep track of manuallly added product links."""
    name = models.CharField(max_length=100)
    filter_name = models.CharField(max_length=100, blank=True, null=True)
    link = models.TextField()
    thumb_url = models.TextField(blank=True, null=True)
    thumb_image = models.TextField(blank=True, null=True)
    active = models.NullBooleanField(null=True, blank=True, default=False)
    category = models.ForeignKey('MainCategory', blank=True, null=True)
    provider = models.ForeignKey('Provider', blank=True, null=True)
    objects = ProductLinksManager()
    @property
    def thumb(self):
        if self.thumb_url:
            return self.thumb_url
        return self.thumb_image
    def get_absolute_url(self):
        return reverse('productlink_detail', kwargs={'pk': self.pk})
    def __str__(self):
        return str(self.name)
    def __unicode__(self):
        return unicode(self.name)
    def save(self):
        self.filter_name = self.name.replace(' ', '-')\
                                    .replace('.', '-')\
                                    .replace('&', '-and-')\
                                    .replace('$', '')\
                                    .replace("'", "")\
                                    .replace('"', '').lower()
        super(ProductLinks, self).save()
    
    
