"""
Set the static class views for admin functionality.
"""
import logging
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from models import Website, WebsitePage, RecentSearches, Provider, MainCategory, ProductLinks
from forms import WebsiteForm, WebsitePageForm, RecentSearchesForm, ProviderForm, \
                  MainCategoryForm, ProductLinksForm
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
    form_class = WebsiteForm
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
    form_class = WebsitePageForm
    template_name = "mainweb/websitepage_update.html"
    def get_object(self, queryset=None):
        obj = WebsitePage.objects.get(id=self.kwargs['pk'])
        return obj
    
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
    form_class = RecentSearchesForm
    template_name = "mainweb/recentsearches_update.html"
    
class RecentSearchesDetailView(StaffuserRequiredMixin, DetailView):
    """
    Website-page detail view.
    """
    queryset = RecentSearches.objects.all()
    def get_object(self, **kwargs):
        obj = super(RecentSearchesDetailView, self).get_object(**kwargs)
        return obj


# Provider Pages
class ProviderView(StaffuserRequiredMixin, ListView):
    """
    Shows a list of the Provider.
    """
    model = Provider

class CreateProvider(StaffuserRequiredMixin, CreateView):
    """
    Create a Provider.
    """
    model = Provider

class UpdateProvider(StaffuserRequiredMixin, UpdateInstanceView):
    """
    Updates a Provider
    """
    model = Provider
    form_class = ProviderForm
    template_name = "mainweb/provider_update.html"
    def get_object(self, queryset=None):
        obj = Provider.objects.get(id=self.kwargs['pk'])
        return obj
    
class ProviderDetailView(StaffuserRequiredMixin, DetailView):
    """
    Provider detail view.
    """
    queryset = Provider.objects.all()
    def get_object(self, **kwargs):
        obj = super(ProviderDetailView, self).get_object(**kwargs)
        return obj


# Category Pages
class MainCategoryView(StaffuserRequiredMixin, ListView):
    """
    Shows a list of the Category.
    """
    model = MainCategory

class CreateMainCategory(StaffuserRequiredMixin, CreateView):
    """
    Create a MainCategory.
    """
    model = MainCategory

class UpdateMainCategory(StaffuserRequiredMixin, UpdateInstanceView):
    """
    Updates a MainCategory.
    """
    model = MainCategory
    form_class = MainCategoryForm
    template_name = "mainweb/maincategory_update.html"
    def get_object(self, queryset=None):
        obj = MainCategory.objects.get(id=self.kwargs['pk'])
        return obj
    
class MainCategoryDetailView(StaffuserRequiredMixin, DetailView):
    """
    Category detail view.
    """
    queryset = MainCategory.objects.all()
    def get_object(self, **kwargs):
        obj = super(MainCategoryDetailView, self).get_object(**kwargs)
        return obj



# ProductLinks Pages
class ProductLinksView(StaffuserRequiredMixin, ListView):
    """
    Shows a list of the ProductLinks.
    """
    model = ProductLinks

class CreateProductLinks(StaffuserRequiredMixin, CreateView):
    """
    Create a ProductLinks.
    """
    model = ProductLinks

class UpdateProductLinks(StaffuserRequiredMixin, UpdateInstanceView):
    """
    Updates a ProductLinks
    """
    model = ProductLinks
    form_class = ProductLinksForm
    template_name = "mainweb/category_update.html"
    def get_object(self, queryset=None):
        obj = ProductLinks.objects.get(id=self.kwargs['pk'])
        return obj
    
class ProductLinksDetailView(StaffuserRequiredMixin, DetailView):
    """
    ProductLinks detail view.
    """
    queryset = ProductLinks.objects.all()
    def get_object(self, **kwargs):
        obj = super(ProductLinksDetailView, self).get_object(**kwargs)
        return obj