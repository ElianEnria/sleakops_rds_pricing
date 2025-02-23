from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.pricing.filters import ProductFilter
from apps.pricing.api.serializers.general_serializers import PriceSerializer, ProductSerializer
from apps.pricing.models import Price, Product

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para listar y filtrar instancias RDS con sus precios asociados
    """
    queryset = Product.objects.prefetch_related('prices').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['sku']


class PriceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los precios y tipos de contratación
    """
    queryset = Price.objects.select_related('product').all()
    serializer_class = PriceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['product__sku', 'term_type']