from django import forms
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Max
from .models import MobileInventory, Customer, Expense, Sales

# --- Sales Form for clean borders ---
class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = '__all__'
        widgets = {
            'customer': forms.Select(attrs={'class': 'vForeignKeyRawIdAdminField'}),
            'mobile': forms.Select(attrs={'class': 'vForeignKeyRawIdAdminField'}),
        }

# --- Admin Custom Branding ---
admin.site.site_header = "Phone O Clock Login"
admin.site.site_title = "Phone O Clock"
admin.site.index_title = "Welcome to Phone O Clock Admin"

admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class CustomUserAdmin(UserAdmin): pass

@admin.register(Group)
class CustomGroupAdmin(GroupAdmin): pass

class SalesInline(admin.TabularInline):
    model = Sales
    extra = 0
    readonly_fields = ('purchase_date', 'total_amount', 'balance_amount', 'status')
    can_delete = False

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'is_regular')
    search_fields = ('name',)
    inlines = [SalesInline]

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'date', 'paid_by')

    # Yahan hum edit permission ko control kar rahe hain
    def has_change_permission(self, request, obj=None):
        # Superuser ko hamesha access hogi
        if request.user.is_superuser:
            return True
        # Agar record pehle se exist karta hai (obj is not None), toh edit allow nahi karenge
        if obj is not None:
            return False
        return True




@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    form = SalesForm  # Yeh standard border wali styling layega
    
    fields = (
        'customer', 
        'mobile', 
        'shipment_date', 
        'payment_mode', 
        'total_amount', 
        'paid_amount', 
        'balance_amount', 
        'status', 
        'remarks'
    )
    
    list_display = ('customer_name', 'customer_phone', 'purchase_date', 'total_amount', 'status')
    list_filter = ('payment_mode', 'status', 'customer')

    def customer_name(self, obj):
        return obj.customer.name if obj.customer else "No Customer"
    customer_name.short_description = 'Customer'

    def customer_phone(self, obj):
        return obj.customer.phone if obj.customer else "-"
    customer_phone.short_description = 'Phone'

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj is not None and obj.status == 'Pending'

        

@admin.register(MobileInventory)
class MobileInventoryAdmin(admin.ModelAdmin):
    list_display = ('edit_icon', 'serial_no', 'mobile_name', 'imei_no', 'actual_price', 'sold_price', 'remarks', 'read_status_box', 'updated_by')
    list_display_links = ('serial_no',)
    # autocomplete_fields ke liye search_fields ka hona zaroori hai
    search_fields = ('imei_no', 'mobile_name') 

    def has_add_permission(self, request): return request.user.is_superuser
    def has_change_permission(self, request, obj=None): return request.user.is_superuser
    def has_delete_permission(self, request, obj=None): return request.user.is_superuser

    def edit_icon(self, obj):
        url = reverse('admin:core_mobileinventory_change', args=[obj.pk])
        return mark_safe(f'<a href="{url}" style="text-decoration:none; color:#007bff;">✏️ Edit</a>')
    
    def read_status_box(self, obj):
        style = "display: inline-block; padding: 2px 10px; border-radius: 4px; color: white; font-weight: bold; font-size: 14px; text-align: center; width: 40px;"
        return mark_safe(f'<div style="background-color: {"#27ae60" if obj.remarks_read else "#c0392b"}; {style}">{"✔" if obj.remarks_read else "✘"}</div>')

    def save_model(self, request, obj, form, change):
        if not obj.serial_no:
            max_serial = MobileInventory.objects.aggregate(Max('serial_no'))['serial_no__max']
            obj.serial_no = (max_serial or 0) + 1
        if not request.user.is_superuser: obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)