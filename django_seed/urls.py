from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^preview.html$', TemplateView.as_view(template_name='faker/preview.html'))
)