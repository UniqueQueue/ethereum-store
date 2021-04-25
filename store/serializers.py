from django.db import transaction
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
    good_id = serializers.IntegerField()

    class Meta:
        model = Offer
        fields = '__all__'


class PurchaseSerializer(serializers.ModelSerializer):
    good = GoodSerializer(read_only=True)
    good_id = serializers.IntegerField()

    class Meta:
        model = Purchase
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    purchases = PurchaseSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.purchases.get_queryset().delete()
        purchases = validated_data.pop('purchases', [])
        for purchase in purchases:
            purchase['order'] = instance
            PurchaseSerializer().create(purchase)

        return super().update(instance, validated_data)


class MyOrderSerializer(serializers.ModelSerializer):
    purchases = PurchaseSerializer(many=True, read_only=True)
    offer_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'email', 'purchases', 'status', 'offer_ids']
        extra_kwargs = {'status': {'read_only': True}}

    @staticmethod
    def validate_offer_ids(ids):
        offers_count = Offer.objects.filter(id__in=ids).count()

        if offers_count != len(ids):
            error = {'detail': _('Some offers are not available anymore. Please refresh.')}
            raise serializers.ValidationError(detail=error)

        return ids

    @transaction.atomic
    def create(self, validated_data):
        offer_ids = validated_data.pop('offer_ids')
        offers = Offer.objects.filter(id__in=offer_ids).all()

        instance = super().create(validated_data)
        user = self.context['request'].user
        if not user.is_anonymous:
            instance.user = user
        instance.save()

        purchases = [Purchase.from_offer(offer) for offer in offers]
        for p in purchases:
            p.order = instance
            p.save()

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        offer_ids = validated_data.pop('offer_ids', [])

        if offer_ids:
            offers = Offer.objects.filter(id__in=offer_ids).all()

            instance.purchases.get_queryset().delete()

            purchases = [Purchase.from_offer(offer) for offer in offers]
            for p in purchases:
                p.order = instance
                p.save()

        return super().update(instance, validated_data)
