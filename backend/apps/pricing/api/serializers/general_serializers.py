from rest_framework import serializers

from rest_framework import serializers

from apps.pricing.models import Price, Product

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    prices = PriceSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


