"""
from https://djangosnippets.org/snippets/2594/
"""

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver


class AnonymousUserBackend(ModelBackend):

    def get_all_permissions(self, user_obj, obj=None):
        if user_obj.is_anonymous:
            if not hasattr(user_obj, '_perm_cache'):
                anon_user_name = settings.ANONYMOUS_USER_NAME
                anon_user = User.objects.get(username=anon_user_name)
                user_obj._perm_cache = self.get_all_permissions(anon_user, obj=obj)
            return user_obj._perm_cache
        return super(AnonymousUserBackend, self).get_all_permissions(user_obj, obj=obj)

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username == settings.ANONYMOUS_USER_NAME:
            return
        return super(AnonymousUserBackend, self).authenticate(request, username=username, password=password, **kwargs)

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active and not user_obj.is_anonymous:
            return False
        return perm in self.get_all_permissions(user_obj, obj=obj)


@receiver(pre_save, sender=User)
def disable_anon_user_password_save(sender, **kwargs):
    instance = kwargs['instance']
    if instance.username == settings.ANONYMOUS_USER_NAME:
        raise ValueError("Can't set anonymous user password")
