from django.db import models
from django.utils import timezone
from datetime import datetime

# Create your models here.
class Product(models.Model):
    """
    Modelo para almacenar las características base de una instancia RDS
    """
    sku = models.CharField(max_length=50, primary_key=True)
    product_family = models.CharField(max_length=100, null=True, blank=True)
    database_engine = models.CharField(max_length=50)
    instance_type = models.CharField(max_length=50)
    vcpu = models.IntegerField()
    memory = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.database_engine} - {self.instance_type}"


class Price(models.Model):
    """
    Modelo para almacenar los diferentes tipos de contratación y precios
    """
    TERM_CHOICES = [
        ('OnDemand', 'OnDemand'),
        ('Reserved', 'Reserved')
    ]
    
    LEASE_CONTRACT_LENGTH_CHOICES = [
        ('1yr', '1 Year'),
        ('3yr', '3 Years'),
    ]
    
    PURCHASE_OPTIONS = [
        ('No Upfront', 'No Upfront'),
        ('Partial Upfront', 'Partial Upfront'),
        ('All Upfront', 'All Upfront')
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    term_type = models.CharField(max_length=20, choices=TERM_CHOICES)
    price_per_hour = models.DecimalField(max_digits=20, decimal_places=10)
    lease_contract_length = models.CharField(
        max_length=10, 
        choices=LEASE_CONTRACT_LENGTH_CHOICES,
        null=True, 
        blank=True
    )
    purchase_option = models.CharField(
        max_length=20, 
        choices=PURCHASE_OPTIONS,
        null=True, 
        blank=True
    )
    effective_date = models.DateTimeField()

    class Meta:
        unique_together = ['product', 'term_type', 'lease_contract_length', 'purchase_option']

    @property
    def price_per_month(self):
        return self.price_per_hour * 730

    @property
    def price_per_year(self):
        return self.price_per_hour * 8760

    def __str__(self):
        if self.term_type == 'Reserved':
            return f"{self.product.sku} - {self.term_type} - {self.lease_contract_length} - {self.purchase_option}"
        return f"{self.product.sku} - {self.term_type}"