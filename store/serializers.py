from django.utils.translation import gettext_lazy as _
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


class MyOrderSerializer(serializers.ModelSerializer):
    purchases = PurchaseSerializer(many=True, read_only=True)
    offer_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'email', 'purchases', 'status', 'offer_ids']
        extra_kwargs = {'status': {'read_only': True}}

    @staticmethod
    def validate_offer_ids(ids):
        offers = Offer.objects.filter(id__in=ids).all()
        disabled = [offer for offer in offers if not offer.enabled]

        errors = [{'detail': _('Offer "%(good_name)s"(%(price)s ETH) is no more available.')
                             % {'good_name': offer.good.name, 'price': offer.price}}
                  for offer in disabled]

        if len(offers) != len(ids):
            errors.append({'detail': _('Some offers are not available anymore. Please refresh.')})

        if errors:
            raise serializers.ValidationError(detail=errors)

        return ids

    def create(self, validated_data):
        offer_ids = validated_data.pop('offer_ids')
        offers = Offer.objects.filter(id__in=offer_ids).all()
        purchases = map(Purchase.from_offer, offers)
        purchases = Purchase.objects.bulk_create(purchases)

        instance = super().create(validated_data)
        instance.purchases.set(purchases)
        return instance
