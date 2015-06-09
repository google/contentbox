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

from django import forms
from search.forms import LiveSearchField
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from main.models import Language, Box


class LiveSearchForm(forms.Form):
    box = LiveSearchField(reverse_lazy('main:live_search'), placeholder=_("Look for your favourite Box!"), label="")
    language = forms.ChoiceField(required=False,widget=forms.RadioSelect, choices=())
    content_type = forms.ChoiceField(required=False,widget=forms.RadioSelect, choices=Box.CONTENT_TYPE_CHOICES)

    def __init__(self, *args, **kwargs):
        super(LiveSearchForm, self).__init__(*args, **kwargs)
        self.fields['language'].choices = [(l.id, l.name) for l in Language.objects.all()]

    class Media:
        js = ('search/jquery.livequery.js','search/jquery.autocomplete.js','search/autocomplete_activator.js',)
