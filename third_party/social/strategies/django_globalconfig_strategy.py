from social.strategies.django_strategy import DjangoStrategy
from django.conf import settings
from config.models import SiteConfiguration

class DjangoGlobalConfigStrategy(DjangoStrategy):
    def get_setting(self, name):
        try:
            return getattr(settings, name)
        except:
            return getattr(SiteConfiguration.get_solo(), name.replace('SOCIAL_AUTH_','').lower())