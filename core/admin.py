from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Max
from unfold.admin import ModelAdmin
from .models import MobileInventory, Customer, Expense, Sales

# --- Registering Built-in Auth Models ---
admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    pass

@admin.register(Group)
class CustomGroupAdmin(GroupAdmin, ModelAdmin):
    pass

@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ('name', 'phone', 'is_regular')

    def has_change_permission(self, request, obj=None):
        # Admin sab kuch edit kar sakta hai
        if request.user.is_superuser:
            return True
        # Staff sirf naya record add kar sakta hai, 
        # lekin save hone ke baad edit (change) nahi kar sakta
        if obj is not None:
            return False
        return True

@admin.register(Expense)
class ExpenseAdmin(ModelAdmin):
    list_display = ('description', 'amount', 'date', 'paid_by')

    # Ye function add karein
    def has_change_permission(self, request, obj=None):
        # Agar user superuser hai toh edit kar sakta hai
        if request.user.is_superuser:
            return True
        # Agar staff hai aur object pehle se saved hai (obj is not None), toh edit nahi kar payega
        if obj is not None:
            return False
        return True

@admin.register(Sales)
class SalesAdmin(ModelAdmin):
    list_display = ('purchase_date', 'total_amount', 'paid_amount', 'balance_amount', 'payment_mode', 'status')
    list_filter = ('payment_mode', 'status')

@admin.register(MobileInventory)
class MobileInventoryAdmin(ModelAdmin):
    list_display = (
        'edit_icon', 'serial_no', 'mobile_name', 'imei_no', 'actual_price', 
        'sold_price', 'remarks', 'read_status_box', 'updated_by'
    )
    
    list_display_links = ('serial_no',)

    # --- PERMISSION RESTRICTIONS ---
    def has_view_permission(self, request, obj=None):
        # Staff ko list dekhne ki ijazat de di
        return True

    def has_add_permission(self, request):
        # Add sirf superuser kar payega
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Edit sirf superuser kar payega
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Delete sirf superuser kar payega
        return request.user.is_superuser

    # Baki functions waisay hi rahen ge
    def edit_icon(self, obj):
        url = reverse('admin:core_mobileinventory_change', args=[obj.pk])
        return mark_safe(f'<a href="{url}" style="text-decoration:none; color:#007bff;">✏️ Edit</a>')
    edit_icon.short_description = 'Action'

    def read_status_box(self, obj):
        style = "display: inline-block; padding: 2px 10px; border-radius: 4px; color: white; font-weight: bold; font-size: 14px; text-align: center; width: 40px;"
        if obj.remarks_read:
            return mark_safe(f'<div style="background-color: #27ae60; {style}">✔</div>')
        else:
            return mark_safe(f'<div style="background-color: #c0392b; {style}">✘</div>')
    read_status_box.short_description = 'Read Status'

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ('updated_by',)
        if obj and obj.sold_price:
            return ('serial_no', 'mobile_name', 'imei_no', 'actual_price', 'sold_price', 'remarks', 'remarks_read', 'updated_by')
        return ('serial_no', 'updated_by')

    def save_model(self, request, obj, form, change):
        if not obj.serial_no:
            max_serial = MobileInventory.objects.aggregate(Max('serial_no'))['serial_no__max']
            obj.serial_no = (max_serial or 0) + 1
        if not request.user.is_superuser:
            obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)