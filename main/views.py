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

from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from settings import JAVASCRIPT_TRANSLATION_VERSION
from main.models import Box, Tag, Language
from django.contrib.auth.decorators import login_required
from search.views import live_search_results
from main.forms import LiveSearchForm
from social.apps.django_app.default.models import UserSocialAuth
from oauth2client.client import OAuth2Credentials
from config.models import SiteConfiguration
import httplib2
from apiclient.discovery import build
from django_ajax.decorators import ajax
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page, never_cache
from django.views.i18n import javascript_catalog
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse


def index(request):

    extra_context = {}

    if request.user.is_staff:
        extra_context['boxes'] = Box.objects.select_related('boxtag_set').all()
    else:
        extra_context['boxes'] = Box.published_boxes.select_related('boxtag_set').all()

    extra_context['tags'] = Tag.objects.all()

    extra_context['hide_boxes_link'] = True

    extra_context['search_form'] = LiveSearchForm()

    return render_to_response('main/index.html',
                              extra_context,
                              context_instance=RequestContext(request))


@login_required
@never_cache
def wall(request):

    extra_context = {}

    extra_context['boxes'] = Box.published_boxes.my_boxes(request.user, request.user.is_staff)

    extra_context['hide_my_boxes_link'] = True

    extra_context['search_form'] = LiveSearchForm()

    return render_to_response('main/wall.html',
                              extra_context,
                              context_instance=RequestContext(request))


@login_required
def box_detail(request, slug):

    if request.user.is_staff:
        box = get_object_or_404(Box.objects.select_related('units', 'instructor', 'links'), slug=slug)
    else:
        box = get_object_or_404(Box.published_boxes.select_related('units', 'instructor', 'links'), slug=slug)

    box.register_user(request.user)

    extra_context = {}

    extra_context['box'] = box
    extra_context['box_tags'] = box.get_tags()

    extra_context['search_form'] = LiveSearchForm()

    files = []
    if box.drive_folder_url:
        config = SiteConfiguration.objects.get()

        access_token = UserSocialAuth.get_social_auth_for_user(request.user, provider='google-oauth2').get().tokens
        credentials = OAuth2Credentials(access_token, config.google_oauth2_key,
                                    config.google_oauth2_secret, None, None, None, None)

        # Create an httplib2.Http object and authorize it with our credentials
        http = httplib2.Http()
        http = credentials.authorize(http)

        drive_service = build('drive', 'v2', http=http)

        folder_id = box.drive_folder_url.split("/")[-1]
        page_token = None
        while True:
            try:
                param = {}
                if page_token:
                    param['pageToken'] = page_token
                folder_files = drive_service.files().list(q='\'%s\' in parents' % folder_id, **param).execute()

                files.extend(folder_files['items'])

                page_token = folder_files.get('nextPageToken')
                if not page_token:
                    break
            except:
                break

    extra_context['files'] = files

    return render_to_response('main/box_detail.html',
                              extra_context,
                              context_instance=RequestContext(request))


@ajax
@login_required
@require_POST
def leave_box(request):
    box_id = request.POST.get('box_id','')
    box = get_object_or_404(Box.published_boxes, id=box_id)

    box.unregister_user(request.user)

    redirect = request.POST.get('redirect',False)
    if redirect:
        return HttpResponseRedirect(reverse('main:wall'))

    return {'box_id': box.id}


def filter_published(request, results):
    languages = request.GET.get('languages',False)
    content_types = request.GET.get('content_types',False)
    if languages:
        results.filter(language_id=languages)
    if content_types:
        results.filter(type=content_types)
    return results.filter(published=True)

def live_search(request):
    return live_search_results(request, Box, 'autocomplete_index', limit=3,
        redirect=True, query_converter=filter_published,
        result_item_formatting=
            lambda box: {'value': u'<div>%s / <i>%s</i><img src="%s" class="float-right item-img" /></div>' % (box.title, box.instructor.name, box.language.image.url),
            'result': box.title, })


# The value returned by get_version() must change when translations change.
@cache_page(86400, key_prefix='js18n-%s' % JAVASCRIPT_TRANSLATION_VERSION)
def cached_javascript_catalog(request, domain='djangojs', packages=None):
    return javascript_catalog(request, domain, packages)
