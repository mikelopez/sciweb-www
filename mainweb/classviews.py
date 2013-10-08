import logging
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render
from django.conf import settings
from models import Website, WebsitePage
LOG_ON = getattr(settings, "LOG_ON", False)
from lib.mainlogger import LoggerLog


class AdminIndexView(TemplateView):
    """
    The admin Index view.
    """
    template_name = "mainweb/admin-index.html"


# Websites
class WebsiteView(ListView):
    """
    Shows the list of websites.
    """
    model = Website

class CreateWebsite(CreateView):
    """
    Create a new Website.
    """
    model = Website

class UpdateWebsite(UpdateView):
    """
    Updates a website.
    """
    model = Website
    
class WebsiteDetailView(DetailView):
    """
    Website Detail Page View.
    """
    queryset = Website.objects.all()
    def get_object(self, **kwargs):
        obj = super(WebsiteDetailView, self).get_object(**kwargs)
        return obj


# Website Pages
class WebsitePageView(ListView):
    """
    Shows a list of the website-pages.
    """
    model = WebsitePage

class CreateWebsitePage(CreateView):
    """
    Create a website-page.
    """
    model = WebsitePage

class UpdateWebsitePage(UpdateView):
    """
    Updates a website page.
    """
    model = WebsitePage
    
class WebsitePageDetailView(DetailView):
    """
    Website-page detail view.
    """
    queryset = WebsitePage.objects.all()
    def get_object(self, **kwargs):
        obj = super(WebsitePageDetailView, self).get_object(**kwargs)
        return obj

