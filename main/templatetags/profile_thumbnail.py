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
from social.apps.django_app.default.models import UserSocialAuth
register = template.Library()

@register.filter(name='profile_thumbnail')
# Converts youtube URL into embed HTML
def youtube_embed_url(user):
    try:
        return UserSocialAuth.get_social_auth('google-oauth2',user.email).extra_data['image']['url']
    except:
        return '/static/global/images/placeholder/user.png'
