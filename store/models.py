from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.db import models
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition

from .utils import send_confirmation


class ETHAddress(models.TextField):
    ADDRESS_LENGTH = 42
    default_validators = [RegexValidator(r'[0-9abcdefABCDEF]*'),
                          MinLengthValidator(ADDRESS_LENGTH),
                          MaxLengthValidator(ADDRESS_LENGTH)]


class User(AbstractUser):
    eth_address = ETHAddress(verbose_name=_('Ethereum Address'))


class Settings(models.Model):
    EMAIL_SUBJECT = 'Email Subject'
    EMAIL_BODY = 'Email Body'
    EMAIL_FROM = 'Email From'

    name = models.TextField(verbose_name=_('Name'), unique=True)
    value = models.TextField(verbose_name=_('Value'))


class Good(models.Model):
    name = models.TextField(verbose_name=_('Name'), unique=True)

    class Meta:
        verbose_name = _('Good')


class Offer(models.Model):
    good = models.ForeignKey(verbose_name=_('Good'), to=Good,
                             related_name='offers', on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name=_('Price'), max_digits=12, decimal_places=6)

    class Meta:
        verbose_name = _('Offer')
        unique_together = ('good', 'price')


class Purchase(models.Model):
    good = models.ForeignKey(verbose_name=_('Good'), to=Good,
                             related_name='purchases', on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name=_('Price'), max_digits=12, decimal_places=6)
    order = models.ForeignKey(verbose_name=_('Order'), to='Order',
                              related_name='purchases', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Purchase')
        permissions = [('view_my_purchase', _('View my purchases'))]

    @staticmethod
    def from_offer(offer):
        return Purchase(good=offer.good, price=offer.price)


ANONYMOUS_CAN_BUY = True


class Order(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DR', _('Draft')
        PROCESSING = 'PR', _('Processing')
        CANCELED = 'CA', _('Canceled')
        FINISHED = 'FI', _('Finished')

    user = models.ForeignKey(verbose_name=_('Buyer'), to=settings.AUTH_USER_MODEL,
                             related_name='orders', null=ANONYMOUS_CAN_BUY,
                             db_constraint=not ANONYMOUS_CAN_BUY, on_delete=models.DO_NOTHING)
    email = models.EmailField(verbose_name=_('E-Mail'), db_index=True)
    eth_address = ETHAddress(verbose_name=_('Ethereum Address'), db_index=True)
    status = FSMField(verbose_name=_('status'), choices=Status.choices,
                      default=Status.DRAFT, max_length=2, db_index=True)

    class Meta:
        verbose_name = _('Order')
        permissions = [('view_my_order', _('View my orders')),
                       ('moderate_my_order', _('Moderate my orders'))]

    @transition(field='state', source='+', target=Status.FINISHED,
                permission='store.moderate_order')
    def finish(self):
        send_confirmation(self.email, model_to_dict(self.user))
