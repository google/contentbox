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

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

# Support for allowing social_auth authentication for /admin (django.contrib.admin)
if getattr(settings, 'SOCIAL_AUTH_USE_AS_ADMIN_LOGIN', False):

    def _social_auth_login(self, request, **kwargs):
        if request.user.is_authenticated():
            if not request.user.is_active or not request.user.is_staff:
                raise PermissionDenied()
        else:
            return redirect_to_login(request.get_full_path())

    # Overide the standard admin login form.
    admin.sites.AdminSite.login = _social_auth_login