from django.db import models

# Create your models here.
class Product(models.Model):
    sku = models.CharField(max_length=50, primary_key=True)
    product_family = models.CharField(max_length=100)
    database_engine = models.CharField(max_length=50)
    instance_type = models.CharField(max_length=50)
    vcpu = models.IntegerField()
    memory = models.DecimalField(max_digits=10, decimal_places=2)
    region = models.CharField(max_length=100)
    deployment_option = models.CharField(max_length=50)
    license_model = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.database_engine} - {self.instance_type} ({self.sku})"


class Price(models.Model):
    TERM_CHOICES = [
        ('OnDemand', 'OnDemand'),
        ('Reserved', 'Reserved')
    ]
    
    PURCHASE_OPTIONS = [
        ('No Upfront', 'No Upfront'),
        ('Partial Upfront', 'Partial Upfront'),
        ('All Upfront', 'All Upfront')
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    term_type = models.CharField(max_length=20, choices=TERM_CHOICES)
    lease_contract_length = models.CharField(max_length=10, null=True, blank=True)
    purchase_option = models.CharField(max_length=20, choices=PURCHASE_OPTIONS, null=True, blank=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=5)
    currency = models.CharField(max_length=10, default='USD')
    unit = models.CharField(max_length=10)
    effective_date = models.DateField()

    def __str__(self):
        return f"{self.term_type} - {self.price_per_unit} {self.currency} ({self.unit})"