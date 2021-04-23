from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Good(models.Model):
    name = models.TextField(verbose_name=_('Name'), unique=True)

    class Meta:
        verbose_name = _('Good')


class Offer(models.Model):
    good = models.ForeignKey(verbose_name=_('Good'), to=Good,
                             related_name='offers', on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name=_('Price'), max_digits=12, decimal_places=6)
    enabled = models.BooleanField(verbose_name=_('Enabled'), default=True)

    class Meta:
        verbose_name = _('Offer')


class Purchase(models.Model):
    good = models.ForeignKey(verbose_name=_('Good'), to=Good,
                             related_name='purchases', on_delete=models.CASCADE)
    price = models.FloatField(verbose_name=_('Price'))

    class Meta:
        verbose_name = _('Purchase')

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
    purchases = models.ManyToManyField(Purchase, related_name='orders')
    status = models.TextField(max_length=2, choices=Status.choices)

    class Meta:
        verbose_name = _('Order')
        permissions = [('view_my_order', _('View my orders')),
                       ('moderate_my_order', _('Moderate my orders'))]
