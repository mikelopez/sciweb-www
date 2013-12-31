from django import forms
from django.forms import ModelForm
from models import Website, RecentSearches, WebsitePage, Provider, \
                   MainCategory, ProductLinks

class BaseForm(ModelForm):
    """Providers Custom form"""
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)


class WebsiteForm(BaseForm):
    """Website Custom form"""
    class Meta:
        model = Website

class WebsitePageForm(BaseForm):
    """WebsitePage Custom form"""
    class Meta:
        model = WebsitePage

class RecentSearchesForm(BaseForm):
    """RecentSearches Custom form"""
    class Meta:
        model = RecentSearches

class MainCategoryForm(BaseForm):
    """MainCategory Custom form"""
    class Meta:
        model = MainCategory

class ProviderForm(BaseForm):
    """Provider Custom form"""
    class Meta:
        model = Provider

class ProductLinksForm(BaseForm):
    """ProductLinks Custom form"""
    class Meta:
        model = ProductLinks