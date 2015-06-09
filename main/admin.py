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

from django.contrib import admin
from main.models import Box, Unit, Tag, BoxTag, BoxRegistration,\
    UserTag, Instructor, Link, Language
from django.contrib.admin.options import TabularInline, StackedInline


class TagInline(TabularInline):
    model = BoxTag
    extra = 2

class UnitInline(StackedInline):
    model = Unit
    extra = 4

class LinkInline(StackedInline):
    model = Link
    extra = 2

class BoxAdmin(admin.ModelAdmin):
    inlines = [
        TagInline,
        UnitInline,
        LinkInline
    ]
    list_display = ('__unicode__', 'published', )
    list_filter = ('published', 'instructor', )
    affix = True

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            if not obj.creator:
                obj.creator = request.user
        elif not change:
            obj.published = False
            if request.user.is_staff:
                obj.creator = request.user
        obj.save()

    def queryset(self, request):
        qs = super(BoxAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(creator=request.user)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ['slug']
        if not request.user.is_superuser:
            self.exclude.extend(['published', 'creator'])
        return super(BoxAdmin, self).get_form(request, obj, **kwargs)


admin.site.register(Box,BoxAdmin)
admin.site.register(Instructor)

admin.site.register(Unit)


class TagAdmin(admin.ModelAdmin):
    exclude = ('slug',)

admin.site.register(Tag,TagAdmin)

admin.site.register(BoxRegistration)

admin.site.register(UserTag)


class LanguageAdmin(admin.ModelAdmin):
    exclude = ('slug',)

admin.site.register(Language,LanguageAdmin)