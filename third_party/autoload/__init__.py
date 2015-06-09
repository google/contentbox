def autodiscover(module_name):
    """
    Automatically loads modules specified by module_name for each app in
    installed apps.
    """
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's module.
        try:
            import_module('%s.%s' % (app, module_name))
        except:
            # Decide whether to bubble up this error. If the app just
            # doesn't have an module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, module_name):
                raise
