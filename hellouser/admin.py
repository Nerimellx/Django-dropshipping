from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from hellouser.models import Products, Customers, Suppliers, FreightPackingType, Waybill, \
    WaybillProducts, WaybillFreightPacking, MyUser


# Register your models here.


class WayBillProductsInline(admin.TabularInline):
    model = WaybillProducts
    fields = ('product', 'price_value', 'quantity')
    list_display = ('product', 'price_value', 'quantity')
    extra = 1


class WayBillAdmin(admin.ModelAdmin):
    list_display = ('number', 'receiver', 'consignor', 'waybill_description')
    fields = ('number', 'receiver', 'consignor', 'waybill_description')
    inlines = [
        WayBillProductsInline
    ]


admin.site.register(MyUser, UserAdmin)
admin.site.register(Products)
admin.site.register(Customers)
admin.site.register(Suppliers)
admin.site.register(FreightPackingType)
admin.site.register(Waybill, WayBillAdmin)
# admin.site.register(WaybillProducts)
admin.site.register(WaybillFreightPacking)
