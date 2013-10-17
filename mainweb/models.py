from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.conf import settings

SHOP_SEARCH = 'shopsearch'
SHOP_COMPARE = 'shopcompare'
SHOP_CATEGORY = 'shopcategory'

# static pages are pages that produce a list view with custom functionality
sp = ['products', 'articles']
# static arg pages would be a detail view of an object, but require a pk value 
sap = ['p', 'search', 'a', 
       SHOP_SEARCH, SHOP_COMPARE, SHOP_CATEGORY]

STATIC_PAGES = getattr(settings, "STATIC_PAGES", sp)
STATIC_ARG_PAGES = getattr(settings, "STATIC_ARG_PAGES", sap)

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
    objects = WebsiteManager()
    
    def __str__(self):
        return str(self.domain)

    def __unicode__(self):
        return unicode(self.domain)

    def get_absolute_url(self):
        return reverse('website-detail', kwargs={'pk': self.pk})

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
    name = models.CharField(max_length=20, default='index')
    type = models.CharField(max_length=15, choices=PAGETYPES, default='sub-landing')
    template = models.CharField(max_length=50, blank=True, null=True)
    redirects_to = models.CharField(**custom_blankfield)
    class Meta:
        ordering = ('website',)

    def __str__(self):
        return str("%s / %s" % (self.website.domain, self.name))

    def __unicode__(self):
        return unicode("%s / %s" % (self.website.domain, self.name))

    def get_absolute_url(self):
        return reverse('websitepage-detail', kwargs={'pk': self.pk})

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

        # do not allow page names of static URLS
        if self.name in STATIC_PAGES:
            self.type = 'static'
            #raise ValidationError('Page name cannot be in static pages: %s' % str([x for x in STATIC_PAGES]))
        if self.name in STATIC_ARG_PAGES:
            self.type = 'static-arg'
            #raise ValidationError('Page name cannot be in static pages: %s' % str([x for x in STATIC_ARG_PAGES]))
        # make sure name is a static arg page or notify available static arg page names
        if self.type == 'static-arg':
            if not self.name in STATIC_ARG_PAGES:
                raise ValidationError('Name not in static arg pages, select a different page type. \
                    Allowed Static Arg Pages are: %s' % STATIC_ARG_PAGES)
            
        # just incase
        if not self.type:
            self.type = self.PAGETYPES[0][0]
        super(WebsitePage, self).save(*args, **kwargs)





