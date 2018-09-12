from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from hellouser.models import Products, Customers, Suppliers, FreightPackingType, Waybill, \
    WaybillProducts, WaybillFreightPacking, MyUser


# Register your models here.


class WayBillProductsInline(admin.TabularInline):
    model = WaybillProducts
    fields = ('product', 'price_value', 'quantity', 'row_number')
    list_display = ('product', 'price_value', 'quantity', 'row_number')
    extra = 1


class WaybillFreightPackingInline(admin.TabularInline):
    model = WaybillFreightPacking
    fields = ('row_number', 'freight_packing', 'weight', 'width', 'height', 'length', 'barcode', 'verified',)
    list_display = ('row_number', 'freight_packing', 'weight', 'width', 'height', 'length', 'barcode', 'verified')
    extra = 1


class WayBillAdmin(admin.ModelAdmin):
    list_display = ('number', 'receiver', 'consignor', 'waybill_description')
    fields = ('number', 'receiver', 'consignor', 'waybill_description')
    inlines = [
        WayBillProductsInline,
        WaybillFreightPackingInline
    ]


class MyUserAdmin(admin.ModelAdmin):
#    fields = ('address', 'address_optional', 'country', 'city', 'zip', 'shipping_address_optional', 'shipping_address',
#              'shipping_country', 'shipping_city', 'shipping_zip',)
    list_display = ('username','email','first_name', 'last_name','address', )



admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Products)
admin.site.register(Customers)
admin.site.register(Suppliers)
admin.site.register(FreightPackingType)
admin.site.register(Waybill, WayBillAdmin)
# admin.site.register(WaybillProducts)
admin.site.register(WaybillFreightPacking)
