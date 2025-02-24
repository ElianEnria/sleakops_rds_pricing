import requests
import logging
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils import timezone
from apps.pricing.models import Product, Price
from datetime import datetime

logger = logging.getLogger(__name__)


def sync_rds_pricing_data():
    """
    Sincroniza los datos de precios de RDS desde la API de AWS
    con manejo de errores, validaciones y operaciones bulk
    """
    url = "https://sleakops-interview-tests.s3.us-east-1.amazonaws.com/rds_us_east_1_pricing.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {str(e)}")
        return "Error en la obtención de datos"

    try:
        data = response.json()
    except ValueError as e:
        logger.error(f"Error parsing JSON: {str(e)}")
        return "Error en formato de datos"

    # Preprocesar fechas y conversiones
    effective_date_cache = {}
    
    try:
        with transaction.atomic():
            current_skus = set()
            
            # Procesar productos en batch
            products_to_update = []
            for sku, product in data['products'].items():
                current_skus.add(sku)
                attrs = product['attributes']
                
                try:
                    product_data = {
                        'product_family': product.get('productFamily', 'Unknown'),
                        'database_engine': attrs.get('databaseEngine', ''),
                        'instance_type': attrs.get('instanceType', ''),
                        'vcpu': int(attrs.get('vcpu', 0)),
                        'memory': _parse_memory(attrs.get('memory', '0'))
                    }
                    products_to_update.append((sku, product_data))
                except (ValueError, InvalidOperation, KeyError) as e:
                    logger.warning(f"Error procesando producto {sku}: {str(e)}")
                    continue

            # Bulk update/create products
            existing_products = {
                p.sku: p for p in Product.objects.filter(sku__in=current_skus)
            }
            
            products_to_create = []
            for sku, defaults in products_to_update:
                if sku in existing_products:
                    product = existing_products[sku]
                    for key, value in defaults.items():
                        setattr(product, key, value)
                    product.save()
                else:
                    products_to_create.append(Product(sku=sku, **defaults))
            
            if products_to_create:
                Product.objects.bulk_create(products_to_create)

            # Eliminar productos obsoletos
            Product.objects.exclude(sku__in=current_skus).delete()

            # Procesar precios
            _process_pricing_data(data, current_skus)

    except Exception as e:
        logger.error(f"Error en transacción: {str(e)}")
        return "Error en procesamiento de datos"

    return "Datos sincronizados correctamente"

def _parse_memory(memory_str):
    """Convierte cadena de memoria a Decimal con validación"""
    try:
        return Decimal(memory_str.split()[0])
    except (IndexError, InvalidOperation, AttributeError) as e:
        logger.warning(f"Error parsing memory: {memory_str} - {str(e)}")
        return Decimal(0)

def _process_pricing_data(data, current_skus):
    """Procesa términos de precios eliminando precios antiguos antes de insertar nuevos registros."""
    for term_type in ['OnDemand', 'Reserved']:
        for sku, terms in data['terms'][term_type].items():
            if sku not in current_skus:
                continue

            try:
                product = Product.objects.get(sku=sku)
            except Product.DoesNotExist:
                continue

            # Eliminar precios antiguos del SKU para el tipo de término específico
            Price.objects.filter(product=product, term_type=term_type).delete()

            new_prices = []

            for term in terms.values():
                try:
                    effective_date = timezone.make_aware(
                        datetime.strptime(term['effectiveDate'], '%Y-%m-%dT%H:%M:%SZ')
                    )
                except (KeyError, ValueError) as e:
                    logger.warning(f"Fecha inválida en término {term}: {str(e)}")
                    continue

                for price_dim in term.get('priceDimensions', {}).values():
                    try:
                        price = Decimal(price_dim['pricePerUnit']['USD'])
                    except (KeyError, InvalidOperation) as e:
                        logger.warning(f"Precio inválido en {sku}: {str(e)}")
                        continue

                    rate_code = price_dim.get('rateCode', None)
                    # Opcional: extraer rangos si son necesarios
                    begin_range = price_dim.get('beginRange', None)
                    end_range = price_dim.get('endRange', None)
                    description = price_dim.get('description', None)
                    
                    price_data = Price(
                        product=product,
                        term_type=term_type,
                        price_per_hour=price,
                        lease_contract_length=term.get('termAttributes', {}).get('LeaseContractLength', ''),
                        purchase_option=term.get('termAttributes', {}).get('PurchaseOption', ''),
                        effective_date=effective_date,
                        rate_code=rate_code,
                        begin_range=begin_range,
                        end_range=end_range,
                        description=description
                    )
                    new_prices.append(price_data)

            # Crear nuevos precios en bulk para este SKU y term_type
            if new_prices:
                Price.objects.bulk_create(new_prices)