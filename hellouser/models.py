# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
  address = models.CharField(max_length=100, default='', blank=False, verbose_name='Адрес')
  address_optional = models.CharField(max_length=100, default='', blank=True, verbose_name='Дополнительный Адрес')
  country = models.CharField(max_length=100, default='', blank=False, verbose_name='Страна')
  city = models.CharField(max_length=100, default='', blank=False, verbose_name='Город')
  zip = models.CharField(max_length=100, default='', blank=False, verbose_name='Почтовый индекс')
  shipping_address_optional = models.CharField(max_length=100, default='', blank=True,
                                               verbose_name='Дополнительный Адрес отправки')
  shipping_address = models.CharField(max_length=100, default='', blank=True,
                                       verbose_name='Адрес отправки')
  shipping_country = models.CharField(max_length=100, default='', blank=True, verbose_name='Страна отправки')
  shipping_city = models.CharField(max_length=100, default='', blank=True, verbose_name='Город отправки')
  shipping_zip = models.CharField(max_length=100, default='', blank=True, verbose_name='Почтовый индекс отправки')

  class Meta:
      verbose_name = 'Пользователь'
      verbose_name_plural = 'Пользователи'

default_char_field_length = 255


# Create your models here.
class BaseModel(models.Model):
    updated = models.DateTimeField(auto_now=True, db_index=True)
    source = models.CharField(max_length=default_char_field_length, default='')

    @classmethod
    def table_fields(cls, *args, **kwargs):
        # Выбираю поля модели (часть полей потом надо будет спрятать)
        # is_relation - это потому, что стандартная get_fields возвращает все, даже ссылки из других табиц на текущую
        columns = [
            f.name
            for f in cls._meta.get_fields()
            if not f.is_relation
               or f.one_to_one
               or (f.many_to_one and f.related_model)
        ]

        # Надо скрыть (не отображать) поля, по которым установлен фильтр. В большинстве случаев это родитель.
        # Нет смысла показывать родителя, если по нему и так отфильтровались. В формах родитель устанавливаетя автоматически
        #  и его нельзя изменить
        hidden_fields = list(kwargs.get('filter_keys', None))
        # Также скрываю служебные поля ('id' и '..._clean' поля): добавляю их к списку фильтров
        hidden_fields += ['id'] + [col + '_clean' for col in BaseModel.clean_fields()]

        return [
            # возвращаю колонку, если она не попала в скрытые поля
            column for column in columns
            # если колонка не в скрытых полях
            if column not in hidden_fields
        ]

    def get_updated(self):
        return self.updated.strftime('%d-%b-%Y %H:%M:%S, ') + self.source

    class Meta:
        abstract = True  # данное поле указывает, что класс абстрактный и что для него не нужно создавать таблицу


class Products(BaseModel):
    """
    Товары компании, которые формируют торговый ассортимент. Обычно выгружаются из учетной системы.
    """
    sku = models.CharField(max_length=default_char_field_length, default='', verbose_name='SKU')
    article = models.CharField(max_length=default_char_field_length, default='', verbose_name='Артикул товара')
    brand = models.CharField(max_length=default_char_field_length, default='', verbose_name='Бренд')
    name = models.CharField(max_length=default_char_field_length, default='', verbose_name='Название товара')

    weight = models.DecimalField(max_digits=15, decimal_places=3, default=0, blank=True, verbose_name='Вес единицы')
    width = models.DecimalField(max_digits=15, decimal_places=3, default=0, blank=True, verbose_name='Ширина единицы')
    height = models.DecimalField(max_digits=15, decimal_places=3, default=0, blank=True, verbose_name='Высота единицы')
    length = models.DecimalField(max_digits=15, decimal_places=3, default=0, blank=True, verbose_name='Длина единицы')

    receiver = models.ForeignKey('Customers', default=None, null=True,
                                 verbose_name="Получатель груза (покупатель)", on_delete=models.CASCADE)

    description = models.CharField(max_length=512, default='', blank=True, verbose_name='Описание товара')

    def get_volume(self):
        # объем одной единицы товара
        return self.width * self.height * self.length

    class Meta:
        db_table = 'products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def save(self, *args, **kwargs):
        super(Products, self).save(*args, **kwargs)

    def __str__(self):
        return u"{0}".format(self.name)


class Customers(BaseModel):
    name = models.CharField(max_length=default_char_field_length, default='', verbose_name='Название товара')
    phone_number = PhoneNumberField(verbose_name = 'Телефон', blank = False)
    address = models.CharField(verbose_name='Адрес', max_length=255, blank=False)
    lat = models.DecimalField(verbose_name='Широта', max_digits=9, decimal_places=7, blank=True, null=True, default=0)
    lon = models.DecimalField(verbose_name='Долгота', max_digits=10, decimal_places=7, blank=True, null=True, default=0)

    class Meta:
        db_table = 'customers'
        verbose_name = 'Заказчик'
        verbose_name_plural = 'Заказчики'


class Suppliers(BaseModel):
    name = models.CharField(max_length=default_char_field_length, default='', verbose_name='Название товара')
    phone_number = PhoneNumberField(verbose_name = 'Телефон', blank = False)
    address = models.CharField(verbose_name='Адрес', max_length=255, blank=False)
    lat = models.DecimalField(verbose_name='Широта', max_digits=9, decimal_places=7, blank=True, null=True, default=0)
    lon = models.DecimalField(verbose_name='Долгота', max_digits=10, decimal_places=7, blank=True, null=True, default=0)

    class Meta:
        db_table = 'suppliers'
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'


# --------------- drop shiping --------------------
class FreightPackingType(BaseModel):
    name = models.CharField(max_length=default_char_field_length, default='', unique=True,verbose_name="Название")

    class Meta:
        verbose_name = 'Транспортная упаковка'
        verbose_name_plural = 'Транспортные упаковки'
        db_table = 'transport_packaging'


class Document(BaseModel):

    number = models.CharField(max_length=default_char_field_length, default='', unique=True,
                              verbose_name="Номер документа")
    editable = models.BooleanField(default=True, verbose_name='Документ может редактирвоаться')

    class Meta:
        abstract = True


class RowTable(BaseModel):
    row_number = models.IntegerField(verbose_name='Номер строки в документе')

    def get_next_number(self):
        # Получить следующий номер строки
        return None

    def add(self):
        # Добавить новую строку
        # При добавлении берется последний номер строки и добавляет новая строка в номером +1
        return None

    def delete(self):
        # Удаляется текущая строка, все строки, которые после нее - пересчитываются номера
        return None

    def copy(self):
        # скопировать строку
        # берется текущая строка, все данные из нее и копируются.
        # Номер строки должен также итерироваться как при добавлении
        return None

    def move_up(self):
        # поднять строку вверх
        return None

    def move_down(self):
        # опустить вниз строку вверх
        return None

    class Meta:
        abstract = True  # данное поле указывает, что класс абстрактный и что для него не нужно создавать таблицу
        verbose_name = 'Табличная часть'
        verbose_name_plural = 'Табличные части'


class ProductDocTable(RowTable):
    # parent = models.IntegerField(default=145, verbose_name='Ссылка на документ')
    product = models.ForeignKey('Products', default=None, null=True, verbose_name='Товар', on_delete=models.CASCADE)
    price_value = models.DecimalField(max_digits=15, decimal_places=5, default=0, verbose_name='Цена товара')
    quantity = models.DecimalField(max_digits=15, decimal_places=5, default=0, verbose_name='Количество товара')

    def get_weight(self):
        # Получить вес товара
        return None

    def get_volume(self):
        # Получить объем товара
        return None

    def get_total_value(self):
        # Получить сумму по строке товара
        return None

    class Meta:
        abstract = True  # данное поле указывает, что класс абстрактный и что для него не нужно создавать таблицу
        verbose_name = 'Табличная часть Товары'
        verbose_name_plural = 'Табличная часть Товары'


class FreightPackingDocTable(RowTable):
    # parent = models.IntegerField(default=145, verbose_name='Ссылка на документ')
    freight_packing = models.ForeignKey('FreightPackingType', default=None, null=True,
                                        verbose_name='Транспортная упаковка', on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=15, decimal_places=3, default=0, blank=True, verbose_name='Вес ТУ')
    width = models.DecimalField(max_digits=15, decimal_places=3, default=0, blank=True, verbose_name='Ширина ТУ')
    height = models.DecimalField(max_digits=15, decimal_places=3, default=0, blank=True, verbose_name='Высота ТУ')
    length = models.DecimalField(max_digits=15, decimal_places=3, default=0, blank=True, verbose_name='Длина ТУ')
    barcode = models.CharField(verbose_name='ШтрихКод', max_length=32)
    verified = models.BooleanField(default=True, verbose_name='Груз проверен')

    def get_weight(self):
        # Получить вес упаковки
        return None

    def get_volume(self):
        # Получить объем упаковки
        return None

    class Meta:
        abstract = True  # данное поле указывает, что класс абстрактный и что для него не нужно создавать таблицу
        verbose_name = 'Табличная часть Транспортные упаковки'
        verbose_name_plural = 'Табличная часть Транспортные упаковки'


class Waybill(Document):
    """
    Таблица 'ТТН' - первый документ в цепочке документооборота
    """
    receiver = models.ForeignKey('Customers', default=None, null=True,
                                 verbose_name="Получатель груза (покупатель)", on_delete=models.CASCADE)
    consignor = models.ForeignKey('Suppliers', default=None, null=True,
                                 verbose_name="Отправитель груза (поставщик)", on_delete=models.CASCADE)
    waybill_description = models.CharField(max_length=512, default='', blank=True, verbose_name='Описание состава отправления')


    def get_weight(self):
        # Получить вес отправления
        return None

    def get_volume(self):
        # Получить объем отправления
        return None

    class Meta:
        db_table = 'waybill'
        verbose_name = 'ТТН'
        verbose_name_plural = 'ТТН'

    def __str__(self):
        return u"{0}".format(self.number)

    def save(self, *args, **kwargs):
        super(Waybill, self).save(*args, **kwargs)


class WaybillProducts(ProductDocTable):
    """
    Табличная часть документа ТТН
    """
    parent = models.ForeignKey('Waybill', default=None, null=True,verbose_name="Документ,"
                                                                                    " владелец табличной части",
                               on_delete=models.CASCADE)

    class Meta:
        db_table = 'waybill_products'
        verbose_name = 'Товар в ТТН'
        verbose_name_plural = 'Товары в ТТН'

    def __str__(self):
        return u"{0}".format(self.number)

    def save(self, *args, **kwargs):
        super(WaybillProducts, self).save(*args, **kwargs)


class WaybillFreightPacking(RowTable):
    """
    Табличная часть документа ТТН
    """
    parent = models.ForeignKey('Waybill', default=None, null=True,
                                 verbose_name="Документ, владелец табличной части", on_delete=models.CASCADE)

    class Meta:
        db_table = 'waybill_freight_packing'
        verbose_name = 'Транспортная упаковка в ТТН'
        verbose_name_plural = 'Транспортные упаковки в ТТН'

    def __str__(self):
        return u"{0}".format(self.number)

    def save(self, *args, **kwargs):
        super(WaybillProducts, self).save(*args, **kwargs)
