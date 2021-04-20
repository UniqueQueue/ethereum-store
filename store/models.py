from django.db import models


class Good(models.Model):
    name = models.TextField(verbose_name='Name', unique=True)
    price = models.FloatField(verbose_name='Price')
