from django.contrib import admin
from .models import Currency, Config, Contractor, Company, Customer, Supplier, Country, \
    Warehouse, FreightPackingType, FPIdentified, Unit, Product, \
    OrderDoc, OrderProductTable, AcceptFPUnknownDoc, InspectFPDoc, InspectFPTable, \
    WayBillDoc, WayBillProductTable, AcceptFPUnknownTable, WayBillStatus, InspectProductDoc, InspectProductTable, \
    MyUser, Phone
from django.contrib.contenttypes.admin import GenericTabularInline


class PhoneInline(GenericTabularInline):
    model = Phone
    list_display = ['number']
    fields = ['number']
    extra = 1


class OrderProductInline(admin.TabularInline):
    model = OrderProductTable
    fields = OrderProductTable.form_edit_fields()
    list_display = OrderProductTable.table_fields()
    extra = 1


class PhoneAdmin(admin.ModelAdmin):
    def Telephone_reg_column(self, obj):
        return obj.content_object if obj.content_object else None

    fieldsets = [
        ('Телефоны контрагентов :', {'fields': ['number', 'content_type', 'content_object']}),
    ]

    readonly_fields = ['content_object', 'content_type']

    list_display = Phone.telephones_table_fields()


class OrderAdmin(admin.ModelAdmin):
    list_display = OrderDoc.table_fields()
    fields = OrderDoc.form_edit_fields()
    inlines = [
        OrderProductInline,
    ]


class WaybillProductInline(admin.TabularInline):
    model = WayBillProductTable
    fields = WayBillProductTable.form_edit_fields()
    list_display = WayBillProductTable.table_fields()
    extra = 1


# class WaybillFreightPackingInline(admin.TabularInline):
#     model = WaybillFreightPacking
#     list_display = WaybillFreightPacking.table_fields()
#     fields = WaybillFreightPacking.form_edit_fields()
#     extra = 1


# class FreightPackingAcceptedInline(admin.TabularInline):
#     model = AcceptFPUnknownTable
#     list_display = AcceptFPUnknownTable.table_fields()
#     fields = AcceptFPUnknownTable.form_edit_fields()
#     extra = 1


class WayBillStatusAdmin(admin.ModelAdmin):
    def doc_reg_column(self, obj):
        return obj.doc_reg if obj.doc_reg else None

    list_display = WayBillStatus.table_fields()
    # fields = WayBillStatus.form_edit_fields()
    doc_reg_column.short_description = u'Регистратор'

    fieldsets = [
        (None, {'fields': ['dt', 'wb', 'status', 'desc', 'content_type', 'object_id', 'doc_reg']}),
    ]
    readonly_fields = ['doc_reg']


class WayBillStatusInline(GenericTabularInline):
    model = WayBillStatus
    list_display = WayBillStatus.table_fields()
    fields = WayBillStatus.form_edit_fields()
    extra = 1


class WaybillAdmin(admin.ModelAdmin):
    list_display = WayBillDoc.table_fields()
    fields = WayBillDoc.form_edit_fields()
    inlines = [
        WaybillProductInline,
        # FreightPackingAcceptedInline,
        # WaybillFreightPackingInline,
        # WayBillStatusInline,
    ]

    def get_status(self, obj):
        object_status = WayBillStatus.objects.filter(
            wb=obj
        ).order_by('-dt').first()
        if object_status:
            try:
                return list((filter(lambda x: object_status.status in x, object_status.STATUS)))[0][1]
            except:
                pass
        return 'Нет зарегистрированных статусов'

    get_status.short_description = u'Статус ТТН'

    def get_inline_instances(self, request, obj=None):
        to_return = super(WaybillAdmin, self).get_inline_instances(request, obj)
        # Разрешаем добавлять в связанные таблицы только если ТНТ уже существует
        if not obj:
            # to_return = [x for x in to_return if not isinstance(x, WaybillProductInline)]
            to_return = []
        return to_return


class AcceptFPUnknownTableInline(admin.TabularInline):
    model = AcceptFPUnknownTable
    list_display = AcceptFPUnknownTable.table_fields()
    fields = AcceptFPUnknownTable.form_edit_fields()
    extra = 1


class AcceptFPUnknownDocAdmin(admin.ModelAdmin):
    list_display = AcceptFPUnknownDoc.table_fields()
    fields = AcceptFPUnknownDoc.form_edit_fields()
    inlines = [
        AcceptFPUnknownTableInline,
    ]


class InspectFPTableInline(admin.TabularInline):
    model = InspectFPTable
    list_display = InspectFPTable.table_fields()
    fields = InspectFPTable.form_edit_fields()
    extra = 1


class InspectFPDocAdmin(admin.ModelAdmin):
    list_display = InspectFPDoc.table_fields()
    fields = InspectFPDoc.form_edit_fields()
    inlines = [
        InspectFPTableInline,
    ]


class InspectProductTableInline(admin.TabularInline):
    model = InspectProductTable
    list_display = InspectProductTable.table_fields()
    fields = InspectProductTable.form_edit_fields()
    extra = 1


class InspectProductDocAdmin(admin.ModelAdmin):
    list_display = InspectProductDoc.table_fields()
    fields = InspectProductDoc.form_edit_fields()
    inlines = [
        InspectProductTableInline,
    ]


class ProductAdmin(admin.ModelAdmin):
    list_display = Product.table_fields()
    fields = Product.form_edit_fields()


class CurrencyAdmin(admin.ModelAdmin):
    list_display = Currency.table_fields()
    fields = Currency.form_edit_fields()


class CountryAdmin(admin.ModelAdmin):
    list_display = Country.table_fields()
    fields = Country.form_edit_fields()


class WarehouseAdmin(admin.ModelAdmin):
    list_display = Warehouse.table_fields()
    fields = Warehouse.form_edit_fields()


class FreightPackingTypeAdmin(admin.ModelAdmin):
    list_display = FreightPackingType.table_fields()
    fields = FreightPackingType.form_edit_fields()


class UnitAdmin(admin.ModelAdmin):
    list_display = Unit.table_fields()
    fields = Unit.form_edit_fields()


class FreightPackingAdmin(admin.ModelAdmin):
    list_display = FPIdentified.table_fields()
    fields = FPIdentified.form_edit_fields()
    list_filter = ('fp_type',)


class ContractorAdmin(admin.ModelAdmin):
    list_filter = ('contractor_type', 'country')
    list_display = Contractor.table_fields()
    search_fields = Contractor.table_fields()
    # fields = Contractor.form_edit_fields()
    fieldsets = (
        (None, {
            'fields': (
                ('contractor_type', 'code', 'name'), 'country',
            )
        }),
        ('Наименования', {
            'classes': ('collapse',),
            'fields': (
                'name_legal',
                ('first_name', 'last_name'),
            ),
        }),
        ('Налоговые коды', {
            'classes': ('collapse',),
            'fields': (
                ('tax_number', 'accounting_number'),
            ),
            'description': 'Тут содержатся налоговые данные, необходимые для оформления документов ',
        }),
    )

    inlines = [
        PhoneInline,
    ]


class MyUserAdmin(admin.ModelAdmin):
    #    fields = ('address', 'address_optional', 'country', 'city', 'zip', 'shipping_address_optional', 'shipping_address',
    #              'shipping_country', 'shipping_city', 'shipping_zip',)
    list_display = ('username', 'email', 'first_name', 'last_name', 'address',)


admin.site.site_header = 'Dropshipping (admin-panel)'

admin.site.register(Phone, PhoneAdmin)
admin.site.register(MyUser, MyUserAdmin)
admin.site.register(OrderDoc, OrderAdmin)
admin.site.register(WayBillDoc, WaybillAdmin)
admin.site.register(AcceptFPUnknownDoc, AcceptFPUnknownDocAdmin)
admin.site.register(InspectFPDoc, InspectFPDocAdmin)
admin.site.register(InspectProductDoc, InspectProductDocAdmin)
admin.site.register(WayBillStatus, WayBillStatusAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(FreightPackingType, FreightPackingTypeAdmin)
admin.site.register(FPIdentified, FreightPackingAdmin)
admin.site.register(Company, ContractorAdmin)
admin.site.register(Warehouse, WarehouseAdmin)
admin.site.register(Customer, ContractorAdmin)
admin.site.register(Supplier, ContractorAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register([Config, ])
