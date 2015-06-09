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

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from help.models import ConditionsChapter, FAQ

def faqs(request):

    extra_context = {}

    extra_context['faqs'] = FAQ.objects.all()

    return render_to_response('help/faqs.html',
                              extra_context,
                              context_instance=RequestContext(request))

def terms(request):

    extra_context = {}

    extra_context['termsandconditions'] = ConditionsChapter.objects.all()

    return render_to_response('help/terms-and-conditions.html',
                              extra_context,
                              context_instance=RequestContext(request))

def about(request):

    extra_context = {}

    return render_to_response('help/about.html',
                              extra_context,
                              context_instance=RequestContext(request))
