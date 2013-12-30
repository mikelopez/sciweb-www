"""
Set the static class views for admin functionality.
"""
import logging
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render
from django.conf import settings
from models import Website, WebsitePage, RecentSearches
from forms import WebsiteForm, WebsitePageForm, RecentSearchesForm
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin
LOG_ON = getattr(settings, "LOG_ON", False)


class UpdateInstanceView(UpdateView):
    """Todo:
    update providers and banners classes
    to update views to use base UpdateInstanceView
    """
    def form_valid(self, form):
        self.object = form.save(commit=False)
        clean = form.cleaned_data
        for k, v in clean.items():
            setattr(self.object, k, v)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class AdminIndexView(StaffuserRequiredMixin, TemplateView):
    """
    The admin Index view.
    """
    template_name = "mainweb/admin-index.html"


# Websites
class WebsiteView(StaffuserRequiredMixin, ListView):
    """
    Shows the list of websites.
    """
    model = Website

class CreateWebsite(StaffuserRequiredMixin, CreateView):
    """
    Create a new Website.
    """
    model = Website

class UpdateWebsite(StaffuserRequiredMixin, UpdateInstanceView):
    """
    Updates a website.
    """
    model = Website
    form_class = GalleryForm
    template_name = 'mainweb/website_update.html'
    def get_object(self, queryset=None):
        obj = Website.objects.get(id=self.kwargs['pk'])
        return obj
    
class WebsiteDetailView(StaffuserRequiredMixin, DetailView):
    """
    Website Detail Page View.
    """
    queryset = Website.objects.all()
    def get_object(self, **kwargs):
        obj = super(WebsiteDetailView, self).get_object(**kwargs)
        return obj


# Website Pages
class WebsitePageView(StaffuserRequiredMixin, ListView):
    """
    Shows a list of the website-pages.
    """
    model = WebsitePage

class CreateWebsitePage(StaffuserRequiredMixin, CreateView):
    """
    Create a website-page.
    """
    model = WebsitePage

class UpdateWebsitePage(StaffuserRequiredMixin, UpdateInstanceView):
    """
    Updates a website page.
    """
    model = WebsitePage
    
class WebsitePageDetailView(StaffuserRequiredMixin, DetailView):
    """
    Website-page detail view.
    """
    queryset = WebsitePage.objects.all()
    def get_object(self, **kwargs):
        obj = super(WebsitePageDetailView, self).get_object(**kwargs)
        return obj



# RecentSearches
class RecentSearchesView(StaffuserRequiredMixin, ListView):
    """
    Shows a list of the website-pages.
    """
    model = RecentSearches

class CreateRecentSearches(StaffuserRequiredMixin, CreateView):
    """
    Create a website-page.
    """
    model = RecentSearches

class UpdateRecentSearches(StaffuserRequiredMixin, UpdateInstanceView):
    """
    Updates a website page.
    """
    model = RecentSearches
    
class RecentSearchesDetailView(StaffuserRequiredMixin, DetailView):
    """
    Website-page detail view.
    """
    queryset = RecentSearches.objects.all()
    def get_object(self, **kwargs):
        obj = super(RecentSearchesDetailView, self).get_object(**kwargs)
        return obj

