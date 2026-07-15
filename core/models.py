from django.db import models

class MobileInventory(models.Model):
    serial_no = models.IntegerField(unique=True)
    mobile_name = models.CharField(max_length=100)
    imei_no = models.CharField(max_length=50)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2)
    sold_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remarks = models.TextField(blank=True, null=True)
    remarks_read = models.BooleanField(default=False)
    updated_by = models.CharField(max_length=100, blank=True, null=True)

    # Ise class ke andar tab key daba kar sahi se align karein:
    def __str__(self):
        return str(self.imei_no)

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    is_regular = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Expense(models.Model):
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    paid_by = models.CharField(max_length=50, choices=[('Cash', 'Cash'), ('Bank', 'Bank')])

class Sales(models.Model):
    PAYMENT_MODES = [('Cash', 'Cash'), ('Bank', 'Bank'), ('Credit', 'Loan')]
    STATUS_CHOICES = [('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Completed', 'Completed')]
    
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    mobile = models.ForeignKey(MobileInventory, on_delete=models.SET_NULL, null=True, blank=True)
    purchase_date = models.DateField(auto_now_add=True)
    shipment_date = models.DateField(null=True, blank=True)
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODES, default='Cash')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    remarks = models.TextField(blank=True)



    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
    





    def save(self, *args, **kwargs):
        self.balance_amount = self.total_amount - self.paid_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale: {self.total_amount} | Status: {self.status}"