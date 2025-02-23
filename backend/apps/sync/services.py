import requests
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
from apps.pricing.models import Product, Price

def sync_rds_pricing_data():
    """
    Sincroniza los datos de precios de RDS desde la API de AWS
    """
    url = "https://sleakops-interview-tests.s3.us-east-1.amazonaws.com/rds_us_east_1_pricing.json"
    response = requests.get(url)
    data = response.json()

    for sku, product in data['products'].items():

        attrs = product['attributes']
        
        # Crear o actualizar el producto
        product_instance, _ = Product.objects.update_or_create(
            sku=sku,
            defaults={
                'product_family': product.get('productFamily', 'Unknown'),
                'database_engine': attrs.get('databaseEngine', ''),
                'instance_type': attrs.get('instanceType', ''),
                'vcpu': int(attrs.get('vcpu', 0)),
                'memory': Decimal(attrs.get('memory', '0').split()[0]),
            }
        )

        # Procesar precios OnDemand
        if sku in data['terms']['OnDemand']:
            for term_data in data['terms']['OnDemand'][sku].values():
                for price_dim in term_data['priceDimensions'].values():
                    Price.objects.update_or_create(
                        product=product_instance,
                        term_type='OnDemand',
                        defaults={
                            'price_per_hour': Decimal(price_dim['pricePerUnit']['USD']),
                            'effective_date': timezone.make_aware(datetime.strptime(
                                term_data['effectiveDate'],
                                '%Y-%m-%dT%H:%M:%SZ'
                            ))
                        }
                    )

        # Procesar precios Reserved
        if sku in data['terms']['Reserved']:
            for term_data in data['terms']['Reserved'][sku].values():
                for price_dim in term_data['priceDimensions'].values():
                    Price.objects.update_or_create(
                        product=product_instance,
                        term_type='Reserved',
                        lease_contract_length=term_data['termAttributes'].get('LeaseContractLength', ''),
                        purchase_option=term_data['termAttributes'].get('PurchaseOption', ''),
                        defaults={
                            'price_per_hour': Decimal(price_dim['pricePerUnit']['USD']),
                            'effective_date': timezone.make_aware(datetime.strptime(
                                term_data['effectiveDate'],
                                '%Y-%m-%dT%H:%M:%SZ'
                            ))
                        }
                    )

    return "Datos sincronizados correctamente"