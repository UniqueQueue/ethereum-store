from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django_registration import signals


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        from .initialization import populate_models, handle_new_buyer
        post_migrate.connect(populate_models, sender=self)
        signals.user_registered.connect(handle_new_buyer)
