from django.db import models
from django.core.validators import RegexValidator

imei_validator = RegexValidator(regex=r'^\d{15}$', message="IMEI must be exactly 15 digits.")

class MobileInventory(models.Model):
    serial_no = models.PositiveIntegerField(unique=True, verbose_name="Serial No")
    mobile_name = models.CharField(max_length=100, verbose_name="Mobile Name")
    imei_no = models.CharField(max_length=15, validators=[imei_validator], unique=True, verbose_name="IMEI/SKU")
    actual_price = models.PositiveIntegerField(verbose_name="Actual Price")
    sold_price = models.PositiveIntegerField(null=True, blank=True, verbose_name="Sold Price")
    sold_date = models.DateField(null=True, blank=True, verbose_name="Sale Date")
    
    # New Fields
    remarks = models.TextField(max_length=200, null=True, blank=True, verbose_name="Remarks")
    remarks_read = models.BooleanField(default=False, verbose_name="Read Status")
    updated_by = models.CharField(max_length=50, null=True, blank=True, verbose_name="Updated By")

    def __str__(self):
        return f"{self.serial_no} - {self.mobile_name}"