# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView, RedirectView
from main.views import cached_javascript_catalog

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from yawdadmin import admin_site
admin_site._registry.update(admin.site._registry)


js_info_dict = {
    'packages': ('main',),
}

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    url(r'^jsi18n/$', cached_javascript_catalog, js_info_dict, name='cached_javascript_catalog'),
    (r'^i18n/', include('django.conf.urls.i18n')),


    url(r'^admin/', include(admin_site.urls)),

    url('', include('adminoauthlogin.urls', namespace='adminoauthlogin')),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/',}, name='auth_logout_next'),
    (r'^summernote/', include('django_summernote.urls')),

    (r'^favicon\.ico$', RedirectView.as_view(url='/static/global/favicon.ico')),
    (r'^robots\.txt$', TemplateView.as_view(template_name='main/robots.txt', content_type='text/plain')),
    (r'^sitemap\.xml$', TemplateView.as_view(template_name='main/sitemap.xml', content_type='application/xml')),

    url('', include('main.urls', namespace='main')),
    url('invitations/', include('invitations.urls', namespace='invitations')),
    url('', include('help.urls', namespace='help')),
)
