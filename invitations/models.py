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


class Invitation(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return u"%s" % self.email


import csv
import os.path
from config.models import SiteConfiguration

class InvitationImport(models.Model):
    file = models.FileField(upload_to="video_csv")
    added = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"%s" % os.path.basename(self.file.name)

    class Meta:
        ordering = ['-added']

from django.db.models.signals import post_save
from google.appengine.ext import deferred
def process_csv(sender, instance, created, **kwargs):
    deferred.defer(_process_csv, instance.id)

def _process_csv(instance_id):
    instance = InvitationImport.objects.get(id=instance_id)
    file = csv.reader(instance.file)

    for row in file:
        name = row[0]
        email = row[1]

        try:
            Invitation.objects.get(email=email)
        except Invitation.DoesNotExist:
            Invitation.objects.create(name=name,email=email)

post_save.connect(process_csv, sender=InvitationImport)