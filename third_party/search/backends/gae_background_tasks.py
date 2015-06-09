from django.conf import settings
from django.db import models
from google.appengine.ext import deferred

default_search_queue = getattr(settings, 'DEFAULT_SEARCH_QUEUE', 'default')

def update_relation_index(search_manager, parent_pk, delete):
    # pass only the field / model names to the background task to transfer less
    # data
    app_label = search_manager.model._meta.app_label
    object_name = search_manager.model._meta.object_name
    deferred.defer(update, app_label, object_name, search_manager.name,
        parent_pk, delete, _queue=default_search_queue)

def update(app_label, object_name, manager_name, parent_pk, delete):
    model = models.get_model(app_label, object_name)
    manager = getattr(model, manager_name)
    manager.update_relation_index(parent_pk, delete)