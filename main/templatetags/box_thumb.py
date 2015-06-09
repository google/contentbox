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

import math
from django import template
register = template.Library()

@register.filter(name='preview_position_h')
def preview_position_h(value):
    result = ""

    if value % 5 + 1 > 3:
        result = "from-right"

    return result

@register.simple_tag
def preview_position_v(length, index):
    result = ""

    round = 5 * math.ceil(length/5.0)
    if length > 5 and index > round-5:
        result = "from-bottom"

    return result

@register.filter
def is_registered(box, user):
    return box.is_registered(user)