from rest_framework import serializers

from .models import Good, Offer, Purchase
from .models import Order


class GoodSerializer(serializers.ModelSerializer):

    class Meta:
        model = Good
        fields = '__all__'


class OfferSerializer(serializers.ModelSerializer):
    good = GoodSerializer(read_only=True)

    class Meta:
        model = Offer
        fields = '__all__'


class PurchaseSerializer(serializers.ModelSerializer):
    good = GoodSerializer(read_only=True)

    class Meta:
        model = Purchase
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    purchases = PurchaseSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
