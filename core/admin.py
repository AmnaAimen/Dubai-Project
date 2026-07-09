from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import MobileInventory
from django.db.models import Max
from unfold.admin import ModelAdmin

@admin.register(MobileInventory)
class MobileInventoryAdmin(ModelAdmin):
    list_display = (
        'edit_icon', 'serial_no', 'mobile_name', 'imei_no', 'actual_price', 
        'sold_price', 'remarks', 'read_status_box', 'updated_by'
    )
    
    list_display_links = ('serial_no',)

    # --- PERMISSION RESTRICTIONS ---
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Staff edit nahi kar payega
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    # -------------------------------

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