from apps.pricing.models import Product
import django_filters

class ProductFilter(django_filters.FilterSet):
    database_engine = django_filters.CharFilter(field_name='database_engine', lookup_expr='icontains')
    instance_type = django_filters.CharFilter(field_name='instance_type', lookup_expr='icontains')
    vcpu = django_filters.NumberFilter(field_name='vcpu')
    memory = django_filters.NumberFilter(field_name='memory')

    class Meta:
        model = Product
        fields = ['database_engine', 'instance_type', 'vcpu', 'memory']
