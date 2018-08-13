from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from hellouser.models import Products,Customers,Suppliers,FreightPackingType,Waybill,WaybillProducts,WaybillFreightPacking, MyUser

# Register your models here.
admin.site.register(MyUser)
admin.site.register(User, UserAdmin)
admin.site.register(Products)
admin.site.register(Customers)
admin.site.register(Suppliers)
admin.site.register(FreightPackingType)
admin.site.register(WaybillProducts)
admin.site.register(WaybillFreightPacking)
admin.site.register(Waybill)