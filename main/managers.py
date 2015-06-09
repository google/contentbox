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

from django.db import models

class PublishedBoxesManager(models.Manager):
    def get_query_set(self):
        return super(PublishedBoxesManager,self).get_query_set().filter(published=True)

    def my_boxes(self, user, staff=False):
        from main.models import BoxRegistration
        my_boxes = []
        box_registrations = BoxRegistration.objects.filter(user=user)
        for registration in box_registrations:
            if staff or registration.box.published:
                my_boxes.append(registration.box)

        return my_boxes

    def suggested_boxes(self, user, interests, excluded_boxes):
        from main.models import BoxTag
        suggested_boxes = []
        for interest in interests:
            for boxtag in BoxTag.objects.filter(tag=interest.tag):
                if boxtag.box.published and boxtag.box not in excluded_boxes and boxtag.box not in suggested_boxes:
                    suggested_boxes.append(boxtag.box)

        return suggested_boxes