from django.utils.importlib import import_module
from django.conf import settings

# load all models.py to ensure signal handling installation or index loading
# of some apps 
for app in settings.INSTALLED_APPS:
    try:
        import_module('%s.models' % (app))
    except ImportError:
        pass

class AutoloadMiddleware(object):
    """Empty because the import above already does everything for us"""
    pass
