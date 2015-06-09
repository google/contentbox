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
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from main.managers import PublishedBoxesManager
from uuslug import uuslug
from django.utils.translation import ugettext_lazy as _

class Box(models.Model):
    CODELAB = "codelab"
    TRACKSESSION = "tracksession"
    KEYNOTE = "keynote"
    WORKSHOP = "workshop"

    CONTENT_TYPE_CHOICES = (
                (CODELAB, _("CodeLab")),
                (TRACKSESSION, _("Track Session")),
                (KEYNOTE, _("Keynote")),
                (WORKSHOP, _("Workshop"))
    )

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length = 80)
    image = models.FileField(upload_to='box_images')
    back_image = models.FileField(upload_to='box_back_images')
    type = models.CharField(max_length=15, choices=CONTENT_TYPE_CHOICES)
    description = models.TextField(max_length=1000)
    github_url = models.URLField(blank=True)
    drive_folder_url = models.URLField(blank=True)
    published = models.BooleanField(default=False)
    instructor = models.ForeignKey('main.Instructor')
    language = models.ForeignKey('main.Language')
    creator = models.ForeignKey(User, related_name="boxes", null=True, blank=True, on_delete=models.SET_NULL)

    objects = models.Manager()
    published_boxes = PublishedBoxesManager()

    class Meta:
        verbose_name_plural = "boxes"

    def __unicode__(self):
        return u"%s" % self.title

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self, max_length=80, word_boundary=True)
        super(Box, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('main:box_detail', args=[self.slug])

    def register_user(self, user):
        try:
            BoxRegistration.objects.get(user=user, box=self)
        except BoxRegistration.DoesNotExist:
            BoxRegistration.objects.create(user=user, box=self)

    def unregister_user(self, user):
        BoxRegistration.objects.filter(user=user, box=self).delete()

    def is_registered(self, user):
        try:
            BoxRegistration.objects.get(user=user.id,box=self)
            return True
        except BoxRegistration.DoesNotExist:
            return False

    def get_tags(self):
        tags = []
        box_tags = self.boxtag_set.all()
        for boxtag in box_tags:
            tags.append(boxtag.tag)
        return tags


class Unit(models.Model):
    title = models.CharField(max_length=300)
    video_link = models.URLField()
    order = models.IntegerField()
    box = models.ForeignKey(Box, related_name='units')

    def __unicode__(self):
        return u"%s - %s" % (self.box, self.video_link)

    class Meta:
        ordering = ['order']


class Tag(models.Model):
    title = models.CharField(max_length=50)
    icon = models.FileField(upload_to='tag_images')
    slug = models.SlugField(max_length = 40)
    description = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return u"%s" % self.title

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self, max_length=40, word_boundary=True)
        super(Tag, self).save(*args, **kwargs)


class Link(models.Model):
    title = models.CharField(max_length=50)
    url = models.URLField()
    box = models.ForeignKey(Box, related_name="links")

    def __unicode__(self):
        return u"%s" % self.title


class BoxTag(models.Model):
    box = models.ForeignKey(Box)
    tag = models.ForeignKey(Tag)

    def __unicode__(self):
        return u"%s - %s" % (self.box, self.tag)


class BoxRegistration(models.Model):
    box = models.ForeignKey(Box)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return u"%s - %s" % (self.box, self.user)


class UserTag(models.Model):
    user = models.ForeignKey(User)
    tag = models.ForeignKey(Tag)

    def __unicode__(self):
        return u"%s - %s" % (self.user, self.tag)


class Instructor(models.Model):
    PLATFORM = "platform"
    ENGINEERING = "engineering"
    GDE = "gde"
    GDG = "gdg"
    TECHMAKERS = "techmakers"
    OTHERS = "others"

    AFFILIATION_CHOICES = (
                (PLATFORM, _("Google Developer Platform")),
                (ENGINEERING, _("Google Engineering")),
                (GDE, _("Google Developer Experts")),
                (GDG, _("Google Developers Groups")),
                (TECHMAKERS, _("Women Techmakers")),
                (OTHERS, _("Google Others"))
    )

    name = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=15, choices=AFFILIATION_CHOICES)
    description = models.TextField(max_length=100)
    image = models.FileField(upload_to='instructor_images')
    plus_page_id = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return u"%s" % self.name


class Language(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length = 80)
    short_name = models.CharField(max_length=300, blank=True)
    image = models.FileField(upload_to='language_images')

    def __unicode__(self):
        return u"%s" % self.name

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.name, instance=self, max_length=80, word_boundary=True)
        super(Language, self).save(*args, **kwargs)
