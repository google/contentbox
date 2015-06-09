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

from django import template
from django.conf import settings
register = template.Library()
import re
import urlparse

@register.filter(name='youtube_thumbnail')
# Converts youtube URL into img thumbnail
def youtube_thumbnail(value):
    if value:
        try:
            url_data = urlparse.urlparse(value)
            query = urlparse.parse_qs(url_data.query)
            video = query["v"][0]
            if video:
                img_url = '//img.youtube.com/vi/%s/mqdefault.jpg' % video
                res = "<img width=\"182px\" src=\"\" data-src=\"%s\"/>" % img_url
                return res
        except:
            pass
    return ''

@register.filter(name='youtube_thumbnail_url')
# Converts youtube URL into img thumbnail
def youtube_thumbnail_url(value):
    if value:
        try:
            url_data = urlparse.urlparse(value)
            query = urlparse.parse_qs(url_data.query)
            video = query["v"][0]
            if video:
                img_url = '//img.youtube.com/vi/%s/mqdefault.jpg' % video
                return img_url
        except:
            pass
    return ''

@register.filter(name='youtube_thumbnail_from_id')
# Converts youtube URL into img thumbnail
def youtube_thumbnail_from_id(value):
    return '//img.youtube.com/vi/%s/mqdefault.jpg' % value