from __future__ import unicode_literals
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Sum
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import ugettext_lazy as _


class MyUser(AbstractUser):
    number = PhoneNumberField(verbose_name='Телефон', default='', blank=False)
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


def get_model_name(model):
    return model.__name__


def get_class_fields(cls):
    return cls._meta.get_fields()


class Phone(models.Model):
    number = PhoneNumberField(verbose_name='Телефон', blank=False)
    content_type = models.ForeignKey(ContentType, verbose_name='Тип контрагента', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(verbose_name='id Объекта')
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        db_table = 'telephones'
        verbose_name = 'Телефон'
        verbose_name_plural = 'Телефоны контрагентов'

    @classmethod
    def telephones_table_fields(cls, *args, **kwargs):
        return 'number', 'content_type', 'content_object'

    def __str__(self):
        return u"{0}".format(self.content_object)


# Create your models here.
class BaseModel(models.Model):
    """ Абстракнтый класс, наследуется всеми моделями. Содержит общие поля """
    phones = GenericRelation(Phone)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    source = models.CharField(max_length=180, default='', blank=True)
    desc = models.CharField(max_length=255, default='', blank=True, verbose_name=_('Комментарий'))
    created_by = models.CharField(max_length=180, default='', blank=True, verbose_name=_('Создатель ТТН'))
    code = models.CharField(max_length=20, default='', verbose_name=_('Сервис-код контрагента'))

    @classmethod
    def table_fields(cls, *args, **kwargs):
        # Выбираю поля модели (часть полей потом надо будет спрятать)
        # is_relation - это потому, что стандартная get_fields возвращает все, даже ссылки из других табиц на текущую
        columns = [
            f.name
            for f in get_class_fields(cls)
            if not f.is_relation or f.one_to_one or (f.many_to_one and f.related_model)
        ]

        # Надо скрыть (не отображать) поля, по которым установлен фильтр. В большинстве случаев это родитель.
        # Нет смысла показывать родителя, если по нему и так отфильтровались. В формах родитель устанавливаетя автоматически и его нельзя изменить
        hidden_fields = list(kwargs.get('filter_keys', None))
        # Также скрываю служебные поля ('id' и '...' поля): добавляю их к списку фильтров
        hidden_fields += ['id']

        return [
            # возвращаю колонку, если она не попала в скрытые поля
            column for column in columns
            # если колонка не в скрытых полях
            if column not in hidden_fields
        ]

    @classmethod
    def form_edit_fields(cls):
        return 'desc',

    def get_updated(self):
        return self.updated.strftime('%d-%b-%Y %H:%M:%S, ') + self.source

    def save(self, *args, **kwargs):
        # тут что-то будем писат общее для всех процедур сохранения
        super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class Contractor(BaseModel):
    """Абстрактный класс Контрагенты. Наследуется моделями
     - Компании (Company),
     - Покупателя (Customer)
     - Поставщики (Supplier)"""
    PRIVATE_PERSON = 'PP'
    COMPANY = 'CO'
    INDIVIDUAL_ENTREPRENEUR = 'IE'
    CONTRACTOR_TYPE = (
        (PRIVATE_PERSON, _('Частное лицо')),
        (COMPANY, _('Компания')),
        (INDIVIDUAL_ENTREPRENEUR, _('Частный предприниматель'))
    )
    contractor_type = models.CharField(max_length=2, choices=CONTRACTOR_TYPE, default=PRIVATE_PERSON, null=False,
                                       verbose_name=_('Тип контрагента'),
                                       help_text=_('<details>'
                                                   '<ul>'
                                                   '<li>Частное лицо: заполняем ФИО, ИНН - не обязательно. Наименование  = ФИО</li>'
                                                   '<li>Частный предприниматель: заполняем ФИО, ИНН, полное наименование. Наименование  = ФИО (СПД-ФЛ)</li>'
                                                   '<li>Компания: заполняем Наименование, Полное наименование, ИНН, ЕГРПОУ</li>'
                                                   '</ul>'
                                                   '</details>')
                                       )

    first_name = models.CharField(max_length=20, default='', blank=True, verbose_name=_('Имя'))
    last_name = models.CharField(max_length=40, default='', blank=True, verbose_name=_('Фамилия')
                                 )
    name = models.CharField(max_length=40, default='', blank=False,
                            verbose_name=_('Наименование'),
                            help_text=_(
                                '<details>Название контрагента, используемое внутри предприятия. Например, покупатель может называться<br><b>"Публичное акционерное общество Автотранспортное предприятие 12981",</b>'
                                '<br>но обычно его назвают <b>"АТП-12981".</b>Это и должно быть указано в наименовании.'
                                '<br>Юридическое название указывайте в поле "Полное наименование"</details>')
                            )
    name_legal = models.CharField(max_length=255, default='', blank=True,
                                  verbose_name=_('Полное наименование'),
                                  help_text=_('<details>Юридическое название компании, '
                                              'частного или индивидуального предпринимателя.'
                                              '<br>Для Частный лиц указывайте ФИО полностью'
                                              '<br>Это поле используется при формировании печатных форм документов</details>')
                                  )
    country = models.ForeignKey('hellouser.Country', on_delete=models.SET_NULL, null=True,
                                verbose_name=_('Страна'),
                                help_text=_('Страна происхождения контрагента')
                                )
    tax_number = models.CharField(max_length=20, default='', blank=True,
                                  verbose_name=_('ИНН'),
                                  help_text=_(
                                      '<details>для других страни или не используется или как-то иначе называется</details>')
                                  )
    accounting_number = models.CharField(max_length=20, default='', blank=True,
                                         verbose_name=_('ЕГРПОУ'),
                                         help_text=_(
                                             '<details>для других страни или не используется или как-то иначе называется</details>')
                                         )

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'name', 'tax_number', 'accounting_number', 'name_legal'

    @classmethod
    def form_edit_fields(cls):
        return 'name', 'code', ('contractor_type', 'name_legal'), ('first_name', 'last_name'), \
               ('tax_number', 'accounting_number'), 'desc'

    class Meta:
        abstract = True


class Country(BaseModel):
    """Модель страны"""
    name = models.CharField(max_length=40, default='', blank=False,
                            verbose_name=_('Наименование'), help_text=_('Навзвание страны')
                            )
    abbr_alpha_2 = models.CharField(max_length=2, default='', unique=True, null=True, blank=True,
                                    verbose_name='Alpha-2', help_text=_('Двухбуквенный код')
                                    )
    abbr_alpha_3 = models.CharField(max_length=3, default='', unique=True, null=True, blank=True,
                                    verbose_name='Alpha-3', help_text=_('Трехбуквенный код')
                                    )
    abbr_digit_3 = models.CharField(max_length=3, default='', unique=True, null=True, blank=True,
                                    verbose_name=_('Код'), help_text=_('Цифровой код')
                                    )

    class Meta:
        verbose_name = _('Страна')
        verbose_name_plural = _('Страны')
        db_table = 'country'

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'name', 'abbr_alpha_3'

    @classmethod
    def form_edit_fields(cls):
        return ('name', 'abbr_digit_3'), ('abbr_alpha_2', 'abbr_alpha_3'), 'desc'

    def __str__(self):
        return u"{0}".format(self.name)


class Currency(BaseModel):
    """
    Валюты используются во всех разделах системы.
    """
    name = models.CharField(max_length=25, default='', unique=True,
                            verbose_name=_('Название')
                            )
    iso_code = models.CharField(max_length=4, default='', unique=True,
                                verbose_name=_('ISO код'),
                                help_text=_(
                                    'Международный цифровой код валюты. Например: доллар США - 840, евро - 978.')
                                )
    abbr = models.CharField(max_length=4, default='', unique=True,
                            verbose_name=_('ISO аббр'))
    simbol = models.CharField(max_length=4, default='', unique=True,
                              verbose_name=_('Символ'),
                              help_text=_(
                                  'Международный буквенный код валюты. Например: доллар США - USD, евро - EUR.'))
    # hidden = False - 'могут использовать эту валюту', True - 'не видят эту валюту'))
    hidden = models.BooleanField(default=False,
                                 verbose_name=_('Отображение покупателям'),
                                 help_text=_(
                                     'Если признак установлен - пользователи видят и могут использоваться данную валюту.')
                                 )

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'iso_code', 'abbr', 'name', 'simbol'

    @classmethod
    def form_edit_fields(cls):
        return ('name', 'simbol'), ('iso_code', 'abbr'), 'hidden', 'desc'

    @staticmethod
    def hellouser():
        config = Config.objects.first()
        return config.hellouser_currency

    class Meta:
        verbose_name = _('Валюта')
        verbose_name_plural = _('Валюты')
        db_table = 'currency'

    def __str__(self):
        return u"{0} ({1})".format(self.abbr, self.name)


class Unit(BaseModel):
    """Классификатор единиц измерения"""
    name = models.CharField(max_length=40, default='', blank=False,
                            verbose_name=_('Название единицы'),
                            help_text=_('Название единицы. Например, штука, кг, упаковка')
                            )

    iso_code = models.CharField(max_length=4, default='', unique=True,
                                verbose_name=_('ISO код'),
                                help_text=_('Штука - 796, Килограмм - 166 ')
                                )

    int_code = models.CharField(max_length=4, default='', unique=True,
                                verbose_name=_('ISO код'),
                                help_text=_('Штука - pc, Килограмм - kg')
                                )

    class Meta:
        verbose_name = _('Единица измерения')
        verbose_name_plural = _('Единицы измерений')
        db_table = 'unit'

    def __str__(self):
        return u"{0}".format(self.name)

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'name', 'iso_code', 'int_code',

    @classmethod
    def form_edit_fields(cls):
        return 'name', 'iso_code', 'int_code',


class FreightPackingType(BaseModel):
    """Классификатор типов транспортной упаковки: Мешок, Ящик, Бочка.
    Фактические это классификатор единиц измерения третичной упаковки"""
    name = models.CharField(max_length=40, default='', blank=False,
                            verbose_name=_('Наименование'),
                            help_text=_('Название типа упаковки. Например, ящик, мешок, бочка')
                            )

    class Meta:
        verbose_name = _('Тип места')
        verbose_name_plural = _('Типы мест')
        db_table = 'freight_packing_type'

    def __str__(self):
        return u"{0}".format(self.name)

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'name',

    @classmethod
    def form_edit_fields(cls):
        return 'name',


class Product(BaseModel):
    """Товары (номенклатура)."""
    customer = models.ForeignKey('hellouser.Customer', on_delete=models.PROTECT, default=None,
                                 verbose_name=_('Покупатель'),
                                 )
    manufacturer = models.ForeignKey('hellouser.Supplier', on_delete=models.PROTECT, default=None,
                                     verbose_name=_('Производитель(поставщик)'),
                                     )
    sku = models.CharField(max_length=50, default='', verbose_name='SKU', blank=True, null=True,
                           help_text=_(
                               'Код номенклатуры, используемый во внутреннем учете. Иногда называют Карточкой складского учета.'))
    article = models.CharField(max_length=50, default='', verbose_name=_('Артикул товара'), blank=True, null=True, )
    brand = models.CharField(max_length=50, default='', verbose_name=_('Бренд товара'),
                             help_text=_('Бренд или производитель товара'), blank=True, null=True, )
    name = models.CharField(max_length=150, default='', verbose_name=_('Название товара'))
    HS_code = models.CharField(max_length=50, default='', verbose_name=_('HS-код'), help_text=_('Код ТН ВЭД'),
                               blank=True, null=True, )
    # Первичная упаковка
    primary_package_weight = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                                 verbose_name=_('Вес первичной упаковки'), blank=True, null=True, )
    primary_package_width = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                                verbose_name=_('Ширина первичной упаковки'), blank=True, null=True, )
    primary_package_height = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                                 verbose_name=_('Высота первичной упаковки'), blank=True, null=True, )
    primary_package_length = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                                 verbose_name=_('Длина первичной упаковки'), blank=True, null=True, )
    primary_package_barcode = models.CharField(max_length=32, default='', blank=True, null=True,
                                               verbose_name=_('Штрихкод первичной упаковки'))
    # вторинчая упаковка
    primary_package_index = models.IntegerField(default=0, verbose_name=_('Количество во вторичной упаковке'),
                                                blank=True, null=True, )
    group_package_weight = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                               verbose_name=_('Вес вторичной упаковки'), blank=True, null=True, )
    group_package_width = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                              verbose_name=_('Ширина вторичной упаковки'), blank=True, null=True, )
    group_package_height = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                               verbose_name=_('Высота вторичной упаковки'), blank=True, null=True, )
    group_package_length = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                               verbose_name=_('Длина вторичной упаковки'), blank=True, null=True, )
    group_package_barcode = models.CharField(max_length=32, default='', blank=True, null=True,
                                             verbose_name=_('Штрихкод вторичной упаковки'))
    group_package_index = models.IntegerField(default=0, verbose_name=_('Количество в транспортной упаковке'),
                                              blank=True, null=True, )
    # Транспортная упаковка
    transport_package_weight = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                                   verbose_name=_('Вес транспортной упаковки'), blank=True, null=True, )
    transport_package_width = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                                  verbose_name=_('Ширина транспортной упаковки'), blank=True,
                                                  null=True, )
    transport_package_height = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                                   verbose_name=_('Высота транспортной упаковки'), blank=True,
                                                   null=True, )
    transport_package_length = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                                   verbose_name=_('Длина транспортной упаковки'), blank=True,
                                                   null=True, )
    transport_package_barcode = models.CharField(max_length=32, default='', blank=True, null=True,
                                                 verbose_name=_('Штрихкод транспортной упаковки'))
    how_to_test = RichTextUploadingField(blank=True, verbose_name=_('Что и как тестировать'))

    class Meta:
        db_table = 'product'
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')

    def __str__(self):
        return u"{0}".format(self.name)

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'name', 'customer'

    @classmethod
    def form_edit_fields(cls):
        return ('customer', 'name', 'manufacturer', 'sku', 'article', 'brand', 'HS_code', 'primary_package_weight',
                'primary_package_width', 'primary_package_height', 'primary_package_length', 'primary_package_barcode',
                'primary_package_index',
                'group_package_weight', 'group_package_width', 'group_package_height', 'group_package_length',
                'group_package_barcode', 'group_package_index', 'transport_package_weight', 'transport_package_width',
                'transport_package_height', 'transport_package_length', 'transport_package_barcode', 'how_to_test')


class FPIdentified(BaseModel):
    """Транспортное место - это конкретный ящик или мешок, который был обработан кладовщиками при приемке.
    Транспортное место уже имеет весогабаритные характеристики и штрих-код"""
    fp_type = models.ForeignKey('hellouser.FreightPackingType', on_delete=models.CASCADE, null=True,
                                verbose_name=_('Транспортное место'),
                                help_text=_(
                                    'Идентифицированное транспортное место, для которого уже заданы весогабаритные размеры и штрихкод')
                                )
    weight = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name=_('Вес'))
    width = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name=_('Ширина'))
    height = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name=_('Высота'))
    length = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name=_('Длина'))
    barcode = models.CharField(max_length=32, default='', blank=False, verbose_name=_('Штрихкод'))

    class Meta:
        verbose_name = _('Идентифицированное (обмеряное) место')
        verbose_name_plural = _('Идентифицированные (обмеряные) места')
        db_table = 'freight_packing'

    def __str__(self):
        return u"{0}-{1} ({2})".format(self.fp_type, self.id, self.barcode)

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'fp_type', 'barcode'

    @classmethod
    def form_edit_fields(cls):
        return 'fp_type', 'barcode', 'weight', ('width', 'height', 'length')


class Warehouse(BaseModel):
    """Склады компании, на которых выполняется обработка номенклатуры и транспортных мест.
    Тут выполняются операции:
        склад-отправитель - приемка мест, проверка мест при приемке, проверка товаров при приемке, погрузка мест в контейнер.
        склад-полуатель - приемка контейнера, разгрузка контейнера, приемка мест из контейнера, раскладка мест, выдача мест покупателю"""
    name = models.CharField(max_length=40, default='', blank=True,
                            verbose_name=_('Наименование'), help_text=_('Название склада')
                            )

    country = models.ForeignKey('hellouser.Country', on_delete=models.SET_NULL, null=True,
                                verbose_name=_('Страна'),
                                help_text=_('Страна, где находится склад')
                                )

    class Meta:
        verbose_name = _('Склад')
        verbose_name_plural = _('Склады')
        db_table = 'warehouse'

    def __str__(self):
        return u"{0}".format(self.name)

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'name', 'country'

    @classmethod
    def form_edit_fields(cls):
        return 'name', 'country', 'desc'


class Company(Contractor):
    """Перечень юридических лиц компании. В большинстве случаев используется при подготовке печатных форм официальных документов"""

    class Meta:
        verbose_name = _('Предприятие')
        verbose_name_plural = _('Предприятия')
        db_table = 'company'

    def __str__(self):
        return u"{0}".format(self.name)


class Supplier(Contractor):
    """Поставщики - в большинстве случаев используются для указания Контрагента-отправителя (consignor) грузов.
    Также используются для указания официального поставщка при подготовке печатных форм официальных документов"""

    class Meta:
        verbose_name = _('Поставщик')
        verbose_name_plural = _('Поставщики')
        db_table = 'supplier'

    def __str__(self):
        return u"{0}".format(self.name)


class Customer(Contractor):
    """Покупатели - в большинстве случаев используются для указания Контрагента-получателя (receiver) грузов.
    Также используются для указания официального покупателя при подготовке печатных форм официальных документов"""

    class Meta:
        verbose_name = _('Покупатель')
        verbose_name_plural = _('Покупатели')
        db_table = 'customer'

    def __str__(self):
        return u"{0}".format(self.name)


class Document(BaseModel):
    """Абстрактный класс, содержащий общие поля для электронных документов: Дата, номер, статус"""
    SAVE = 'SV'
    PROCESSED = 'PR'
    MARK_DELETE = 'MD'
    EMPTY = ''
    ALL = 'ALL'
    NOBODY = 'NBD'
    ADMIN_ONLY = 'ADM'
    STATUS_TYPE = (
        (SAVE, _('Сохранен')),
        (PROCESSED, _('Проведен')),
        (MARK_DELETE, _('Помечен на удаление'))
    )
    EDITABLE_FOR = (
        (ALL, _('Разрешено для всех')),
        (NOBODY, _('Запрещено всем')),
        (ADMIN_ONLY, _('Разрешено только администраторам'))
    )

    number = models.CharField(max_length=20, default='', unique=True, verbose_name=_('Номер документа'))

    block = models.CharField(max_length=3, choices=EDITABLE_FOR, default=ALL,
                             verbose_name=_('Редактирование документа'))
    status = models.CharField(max_length=2, choices=STATUS_TYPE, default=SAVE,
                              verbose_name=_('Статус документа'),
                              )
    date_doc = models.DateTimeField(verbose_name=_('Дата документа'),
                                    default=datetime.now)

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'number', 'date_doc', 'status', 'block'

    @classmethod
    def form_edit_fields(cls):
        return 'number', 'status', 'block'

    class Meta:
        abstract = True

    def __str__(self):
        dt = '{:%Y-%m-%d %H:%M}'.format(self.date_doc)
        return u"{0} №{1} от {2}".format(self._meta.verbose_name, self.number, dt)


class RowTableAbstract(BaseModel):
    """Абстрактный класс Табличная часть. Предназначен для создания моделей Табличная часть документа."""
    row_number = models.IntegerField(default=0, verbose_name=_('Номер строки'))
    code = models.IntegerField(default=0, verbose_name=_('Номер строки'))

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'row_number',

    @classmethod
    def form_edit_fields(cls):
        return 'row_number',

    class Meta:
        abstract = True


class ProductTableAbstract(RowTableAbstract):
    """Абстрактный класс Табличная часть Товары. Предназначен для создания моделей табличных частей Товары в документах.
    Т.е. все документы, которые имеют Товары наследуют данный класс"""
    product = models.ForeignKey('hellouser.Product', on_delete=models.PROTECT,
                                verbose_name=_('Товар'),
                                )
    qty = models.FloatField(default=1, verbose_name=_('Количество'))
    HS_code = models.CharField(max_length=50, default='', verbose_name=_('HS-код'), help_text=_('Код ТН ВЭД'),
                               blank=True)
    weight = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name=_('Вес'))
    width = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name=_('Ширина'))
    height = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name=_('Высота'))
    length = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name=_('Длина'))
    barcode = models.CharField(max_length=32, default='', blank=True, verbose_name=_('Штрихкод'))

    def set_wight_volume_product(self):
        self.weight = self.product.group_package_weight
        self.width = self.product.group_package_width
        self.height = self.product.group_package_height
        self.length = self.product.group_package_weight

    def get_total_qty(self):
        pass

    def get_volume(self):
        pass

    def get_total_volume(self):
        pass

    def get_total_weight(self):
        pass

    def get_sum(self):
        pass

    def get_total_sum(self):
        pass

    class Meta:
        abstract = True


class FPTableAbstract(RowTableAbstract):
    """Абстрактный класс Табличная часть Транспортные места. Предназначен для создания моделей табличных частей Транспортные места в документах.
    Т.е. все документы, которые имеют ТРанспортные места наследуют данный класс"""
    fp = models.ForeignKey('hellouser.FPIdentified', on_delete=models.PROTECT, null=True,
                           verbose_name=_('Транспортное место'),
                           )

    def get_total_qty(self):
        pass

    def get_volume(self):
        pass

    def get_total_volume(self):
        pass

    def get_total_weight(self):
        pass

    class Meta:
        abstract = True


class OrderDoc(Document):
    """Электронный документ "Заказ" предназначен для оформления предварительных намерений о перевозке товаров.
    Докмент предназначен в первую очередь для регистрации Номеклатуры, которая будет в дальнейшем использоваться при
    оформлении ТТН"""
    receiver = models.ForeignKey('hellouser.Customer', on_delete=models.SET_NULL, null=True,
                                 verbose_name=_('Получатель'),
                                 )
    consignor = models.ForeignKey('hellouser.Supplier', on_delete=models.SET_NULL, null=True,
                                  verbose_name=_('Отправитель'),
                                  )
    check_product = models.BooleanField(default=False,
                                        verbose_name=_('Проверить товар в заказе'),
                                        )

    currency = models.ForeignKey('hellouser.Currency', on_delete=models.SET_NULL, null=True,
                                 verbose_name=_('Валюта документа'),
                                 )

    class Meta:
        db_table = 'order'
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')

    def create_waybill(self):
        pass

    def __str__(self):
        return u"{0}".format(self.number)

    @classmethod
    def form_edit_fields(cls):
        return 'number', 'date_doc', 'currency', 'status', 'block', 'receiver', 'consignor', 'check_product'


class OrderProductTable(ProductTableAbstract):
    """Табличная часть Товары документ Заказ"""
    doc = models.ForeignKey('hellouser.OrderDoc', on_delete=models.CASCADE, null=True,
                            verbose_name=_('Документ'),
                            help_text=_('Документ, в табличной части, которого данный товар')
                            )
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                verbose_name=_('Цена'))

    class Meta:
        db_table = 'order_product'
        verbose_name = _('Товар в заказе')
        verbose_name_plural = _('Товары в заказах')
        unique_together = ('doc', 'product', 'row_number')

    def get_price_total(self):
        pass

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'product', 'qty', 'price'

    @classmethod
    def form_edit_fields(cls):
        return 'product', 'qty', 'HS_code', 'weight', 'width', 'height', 'length', 'barcode', 'price'


class WayBillDoc(Document):
    """Электронный документ "ТТН" является самым важным документом.
    Фактически это отправная точка для документооборота. На основании ТТН офомрляются все дальнейшие работы на складах,
    Оформление официальных документов"""
    receiver = models.ForeignKey('hellouser.Customer', on_delete=models.SET_NULL, null=True,
                                 verbose_name=_('Получатель'),
                                 )
    consignor = models.ForeignKey('hellouser.Supplier', on_delete=models.SET_NULL, null=True,
                                  blank=True,
                                  verbose_name=_('Отправитель'),
                                  )
    check_product = models.BooleanField(default=False,
                                        verbose_name=_('Проверить товар'),
                                        )
    order = models.ForeignKey('hellouser.OrderDoc', on_delete=models.SET_NULL,
                              verbose_name=_('Заказ'), null=True,
                              blank=True,
                              )

    class Meta:
        db_table = 'waybill'
        verbose_name = _('ТТН')
        verbose_name_plural = _('ТТН')

    # def __init__(self, *args, **kwargs):
    #     super(WayBillDoc, self).__init__(*args, **kwargs)
    #     self.__status_old = self.status

    def get_weight(self):
        pass

    def get_volume(self):
        pass

    def doc_process(self):
        pass
        self.save()

    def clean(self):
        # Если нет статусов или статусы только от WayBill
        object_status = WayBillStatus.objects.filter(
            wb=self
        ).order_by('-dt').first()
        if object_status and object_status.doc_reg != self:
            message = 'Вы не можете изменить статус документа'
            raise ValidationError({'__all__': [message]})

    def save(self, *args, **kwargs):
        super(WayBillDoc, self).save(*args, **kwargs)
        # Удаляем все записи, которые сделал текщий Waybill
        content_type = ContentType.objects.get_for_model(self)
        object_status = WayBillStatus.objects.filter(
            content_type__pk=content_type.pk,
            object_id=self.pk)
        if object_status.exists():
            object_status.delete()

        if self.status == WayBillDoc.PROCESSED:
            # Добавляем статус Проведен
            WayBillStatus.objects.create(
                dt=datetime.now(tz=timezone.utc),
                status=WayBillStatus.WB_ACCEPTED,
                doc_reg=self,
                wb=self,
                desc=_('ТТН проведена в системе')
            )
        #     # Проверяем принятые неидентицицированные места.
        #     # Если есть - пишем статус Приняты места (не проверены)
        #     object_wb_fpa = AcceptFPUnknownTable.objects.filter(
        #         doc=self
        #     )
        #     if object_wb_fpa.exists():
        #         desc = ', '.join(str(x.fp_type.name) + ' = ' + str(x.qty)
        #                          for x in object_wb_fpa)
        #         WayBillStatus.objects.create(
        #             dt=datetime.now(tz=timezone.utc),
        #             status=WayBillStatus.FP_ACCEPTED,
        #             doc_reg=self,
        #             wb=self,
        #             desc=_('Принято на склад: ') + str(desc)
        #         )
        #
        #     # Проверяем есть ли проверенные (обмеряные) места.
        #     # Если есть - пишем статус Места проверены и обмеряны
        #     object_wb_fp = WaybillFreightPacking.objects.filter(
        #         doc=self
        #     )
        #     if object_wb_fp.exists():
        #         desc = ', '.join(str(x.fp_type.fp_type.name)
        #                          for x in object_wb_fp)
        #         WayBillStatus.objects.create(
        #             dt=datetime.now(tz=timezone.utc),
        #             status=WayBillStatus.FP_CHECKED,
        #             doc_reg=self,
        #             wb=self,
        #             desc=_('Проверено: ') + str(desc)
        #         )
        #     # Смотрим, нужно ли проверять товар
        #     # Если нужно, проверяем есть ли товар, и пишем статус Ожидается проверка товара
        #     if self.check_product:
        #         object_wb_p = WayBillProduct.objects.filter(
        #             doc=self
        #         )
        #         if object_wb_p.exists():
        #             tmp = str(object_wb_p.aggregate(total=Sum('qty'))['total'])
        #         else:
        #             tmp = _('нет данных')
        #         WayBillStatus.objects.create(
        #             dt=datetime.now(tz=timezone.utc),
        #             status=WayBillStatus.FP_PRODUCT_WAITING_CHECKING,
        #             doc_reg=self,
        #             wb=self,
        #             desc=_('Ожидается проверка: ') + str(tmp) + _(' товаров')
        #         )
        # # todo сделать запись статуса (FP_PRODUCT_CHECKED, 'Товар проверен'), если заполнена таблица WaybillProductChecked

    @classmethod
    def form_edit_fields(cls):
        return 'number', 'date_doc', 'created_by', 'status', 'block', 'consignor', 'receiver', 'order', 'check_product',\
               'desc', 'source'

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'number', 'date_doc', 'status', 'block', 'get_status'


class WayBillProductTable(ProductTableAbstract):
    """Табличная часть Товары документ ТТН. Тут фиксируются товары, которые Отправитель передает Получателю"""
    doc = models.ForeignKey('hellouser.WayBillDoc', on_delete=models.CASCADE, null=True,
                            verbose_name=_('Документ'),
                            help_text=_('Документ, в табличной части, которого данный товар'),
                            related_name='waybill_product'
                            )
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                verbose_name=_('Прайс'))

    class Meta:
        db_table = 'waybill_product'
        verbose_name = _('Товар в ТТН')
        verbose_name_plural = _('Товары в ТТН')
        unique_together = ('doc', 'product', 'row_number')

    def get_price_total(self):
        pass

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'product', 'qty', 'price'

    @classmethod
    def form_edit_fields(cls):
        return 'product', 'qty', 'HS_code', 'weight', 'width', 'height', 'length', 'barcode', 'price'


class AcceptFPUnknownDoc(Document):
    wb = models.ForeignKey('hellouser.WayBillDoc', on_delete=models.PROTECT,
                           verbose_name=_('ТТН'),
                           help_text=_('ТТН, по которой пересчитываем неидентифицированные места'),
                           related_name='accept_fp_wb'
                           )

    class Meta:
        db_table = 'accept_fp_unknown'
        verbose_name = _('Приемка неидентифицированных мест по ТТН')
        verbose_name_plural = _('Приемки неидентифицированных мест по ТТН')

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'wb',

    @classmethod
    def form_edit_fields(cls):
        return 'wb',

    def clean(self):
        # Если статус Проведен или статусы только от AcceptFPUnknownDoc
        object_status = WayBillStatus.objects.filter(
            wb=self.wb
        ).order_by('-dt').first()
        if not object_status or not (
                object_status and (object_status.status == WayBillStatus.WB_ACCEPTED or object_status.doc_reg == self)):
            message = 'Вы не можете изменить статус документа'
            raise ValidationError({'__all__': [message]})

    def save(self, *args, **kwargs):
        super(AcceptFPUnknownDoc, self).save(*args, **kwargs)
        # Удаляем все записи, которые сделал текщий AcceptFPUnknownDoc
        content_type = ContentType.objects.get_for_model(self)
        object_status = WayBillStatus.objects.filter(
            content_type__pk=content_type.pk,
            object_id=self.pk)
        if object_status.exists():
            object_status.delete()

        # Проверяем принятые неидентицицированные места.
        # Если есть - пишем статус Приняты места (не проверены)
        object_wb_fpa = AcceptFPUnknownTable.objects.filter(
            doc=self
        )
        if object_wb_fpa.exists():
            desc = ', '.join(str(x.fp_type.name) + ' = ' + str(x.qty)
                             for x in object_wb_fpa)
            WayBillStatus.objects.create(
                dt=datetime.now(tz=timezone.utc),
                status=WayBillStatus.FP_ACCEPTED,
                doc_reg=self,
                wb=self.wb,
                desc=_('Принято на склад: ') + str(desc)
            )


class AcceptFPUnknownTable(RowTableAbstract):
    """Табличная часть Принятые транспортные места документа ТТН.
    Тут фиксируются не идентифированные места, общее количество ящиков и мешков. Которые приняли на склад по ТТН"""
    doc = models.ForeignKey('hellouser.AcceptFPUnknownDoc', on_delete=models.CASCADE, null=True,
                            verbose_name=_('Документ'),
                            help_text=_('Документ, в табличной части, которого данное место'),
                            related_name='accept_fp_unknown'
                            )
    fp_type = models.ForeignKey('hellouser.FreightPackingType', on_delete=models.PROTECT, null=True,
                                verbose_name=_('Транспортное место'),
                                )
    qty = models.IntegerField(default=1, verbose_name=_('Количество'))

    class Meta:
        db_table = 'accept_fp_unknown_table'
        verbose_name = _('Неидентифицированное место в ТТН')
        verbose_name_plural = _('Неидентифицированные места в ТТН')
        unique_together = ('doc', 'fp_type', 'row_number')

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'fp_type', 'qty'

    @classmethod
    def form_edit_fields(cls):
        return 'fp_type', 'qty'


class InspectFPDoc(Document):
    wb = models.ForeignKey('hellouser.WayBillDoc', on_delete=models.PROTECT,
                           verbose_name=_('ТТН'),
                           help_text=_('ТТН, по которой обмеряем места'),
                           related_name='inspect_fp_wb'
                           )

    class Meta:
        db_table = 'inspect_fp'
        verbose_name = _('Обмер мест и расклейка ШК по ТТН')
        verbose_name_plural = _('Обмеры мест и расклейка ШК по ТТН')

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'wb',

    @classmethod
    def form_edit_fields(cls):
        return 'wb',

    def clean(self):
        # Если статус Приняты места (не проверены) или статусы только от InspectFPDoc
        object_status = WayBillStatus.objects.filter(
            wb=self.wb
        ).order_by('-dt').first()
        if not object_status or not (
                object_status and (object_status.status == WayBillStatus.FP_ACCEPTED or object_status.doc_reg == self)):
            message = 'Вы не можете изменить статус документа'
            raise ValidationError({'__all__': [message]})

    def save(self, *args, **kwargs):
        super(InspectFPDoc, self).save(*args, **kwargs)
        # Удаляем все записи, которые сделал текщий InspectFPDoc
        content_type = ContentType.objects.get_for_model(self)
        object_status = WayBillStatus.objects.filter(
            content_type__pk=content_type.pk,
            object_id=self.pk)
        if object_status.exists():
            object_status.delete()

        # Проверяем есть ли проверенные (обмеряные) места.
        # Если есть - пишем статус Места проверены и обмеряны
        object_wb_fp = InspectFPTable.objects.filter(
            doc=self
        )
        if object_wb_fp.exists():
            desc = ', '.join(str(x.fp.fp_type.name)
                             for x in object_wb_fp)
            WayBillStatus.objects.create(
                dt=datetime.now(tz=timezone.utc),
                status=WayBillStatus.FP_CHECKED,
                doc_reg=self,
                wb=self.wb,
                desc=_('Проверено: ') + str(desc)
            )
        # Смотрим, нужно ли проверять товар
        # Если нужно, проверяем есть ли товар, и пишем статус Ожидается проверка товара
        if self.wb.check_product:
            object_wb_p = WayBillProductTable.objects.filter(
                doc=self.wb
            )
            if object_wb_p.exists():
                tmp = str(object_wb_p.aggregate(total=Sum('qty'))['total'])
            else:
                tmp = _('нет данных')
            WayBillStatus.objects.create(
                dt=datetime.now(tz=timezone.utc),
                status=WayBillStatus.FP_PRODUCT_WAITING_CHECKING,
                doc_reg=self,
                wb=self.wb,
                desc=_('Ожидается проверка: ' + str(tmp) + ' товаров')
            )
        else:
            WayBillStatus.objects.create(
                dt=datetime.now(tz=timezone.utc),
                status=WayBillStatus.READY_FOR_SHIP,
                doc_reg=self,
                wb=self.wb,
                desc=_('Готов к отправке')
            )


class InspectFPTable(RowTableAbstract):
    """Табличная часть Принятые транспортные места документа ТТН.
    Тут фиксируются не идентифированные места, общее количество ящиков и мешков. Которые приняли на склад по ТТН"""
    doc = models.ForeignKey('hellouser.InspectFPDoc', on_delete=models.CASCADE, null=True,
                            verbose_name=_('Документ'),
                            help_text=_('Документ, в табличной части, которого данное место'),
                            related_name='inspect_fp'
                            )
    fp = models.ForeignKey('hellouser.FPIdentified', on_delete=models.PROTECT, null=True,
                           verbose_name=_('Транспортное место (идент.)'),
                           )
    on_pallet = models.BooleanField(default=False, verbose_name=_('На паллете?'),
                                    help_text=_('Если признак установлен - место пришло в виде паллеты.')
                                    )

    class Meta:
        db_table = 'inspect_fp_table'
        verbose_name = _('Идентифицированное место в ТТН')
        verbose_name_plural = _('Идентифицированные места в ТТН')
        unique_together = ('doc', 'fp')

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'doc', 'fp', 'on_pallet'

    @classmethod
    def form_edit_fields(cls):
        return 'doc', 'fp', 'on_pallet'


class InspectProductDoc(Document):
    fp = models.ForeignKey('hellouser.FPIdentified', on_delete=models.PROTECT, null=True,
                           verbose_name=_('Транспортное место (идент.)'),
                           )

    class Meta:
        db_table = 'inspect_product'
        verbose_name = _('Проверка товара')
        verbose_name_plural = _('Проверка товаров')

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'fp',

    @classmethod
    def form_edit_fields(cls):
        return 'fp',

    # def clean(self):
    #     # Если статус Приняты места (не проверены) или статусы только от InspectFPDoc
    #     object_status = WayBillStatus.objects.filter(
    #         wb=self.wb
    #     ).order_by('-dt').first()
    #     if not object_status or not(object_status and (object_status.status == WayBillStatus.FP_ACCEPTED or object_status.doc_reg == self)):
    #         message = 'Вы не можете изменить статус документа'
    #         raise ValidationError({'__all__': [message]})

    def save(self, *args, **kwargs):
        super(InspectFPDoc, self).save(*args, **kwargs)
        # # Удаляем все записи, которые сделал текщий InspectFPDoc
        # content_type = ContentType.objects.get_for_model(self)
        # object_status = WayBillStatus.objects.filter(
        #     content_type__pk=content_type.pk,
        #     object_id=self.pk)
        # if object_status.exists():
        #     object_status.delete()
        #
        # # Проверяем есть ли проверенные (обмеряные) места.
        # # Если есть - пишем статус Места проверены и обмеряны
        # object_wb_fp = InspectFPTable.objects.filter(
        #     doc=self
        # )
        # if object_wb_fp.exists():
        #     desc = ', '.join(str(x.fp.fp_type.name)
        #                      for x in object_wb_fp)
        #     WayBillStatus.objects.create(
        #         dt=datetime.now(tz=timezone.utc),
        #         status=WayBillStatus.FP_CHECKED,
        #         doc_reg=self,
        #         wb=self.wb,
        #         desc=_('Проверено: ') + str(desc)
        #     )
        # # Смотрим, нужно ли проверять товар
        # # Если нужно, проверяем есть ли товар, и пишем статус Ожидается проверка товара
        # if self.wb.check_product:
        #     object_wb_p = WayBillProductTable.objects.filter(
        #         doc=self.wb
        #     )
        #     if object_wb_p.exists():
        #         tmp = str(object_wb_p.aggregate(total=Sum('qty'))['total'])
        #     else:
        #         tmp = _('нет данных')
        #     WayBillStatus.objects.create(
        #         dt=datetime.now(tz=timezone.utc),
        #         status=WayBillStatus.FP_PRODUCT_WAITING_CHECKING,
        #         doc_reg=self,
        #         wb=self.wb,
        #         desc=_('Ожидается проверка: ' + str(tmp) + ' товаров')
        #     )
        # else:
        #     WayBillStatus.objects.create(
        #         dt=datetime.now(tz=timezone.utc),
        #         status=WayBillStatus.READY_FOR_SHIP,
        #         doc_reg=self,
        #         wb=self.wb,
        #         desc=_('Готов к отправке')
        #     )


class InspectProductTable(RowTableAbstract):
    """Табличная часть Проверка товаров"""
    doc = models.ForeignKey('hellouser.InspectProductDoc', on_delete=models.CASCADE, null=True,
                            verbose_name=_('Документ'),
                            help_text=_('Документ, в табличной части, которого данное место'),
                            related_name='inspect_product'
                            )
    product = models.ForeignKey('hellouser.Product', on_delete=models.PROTECT,
                                verbose_name=_('Товар'),
                                )
    resume = RichTextUploadingField(blank=True, verbose_name=_('Резюме по тестированию'))

    class Meta:
        db_table = 'inspect_product_table'
        verbose_name = _('Проверенный товар в ТТН')
        verbose_name_plural = _('Проверенные товары в ТТН')

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'doc',

    @classmethod
    def form_edit_fields(cls):
        return 'doc', 'product', 'resume',


# class WaybillFreightPacking(FreightPackingTable):
#     """Табличная часть Транспортные места идентифицированные документ ТТН. Тут фиксируются места,
#     в которые уже обмеряли и наклеили штрих-код"""
#     doc = models.ForeignKey('hellouser.WayBill', on_delete=models.PROTECT, null=True,
#                             verbose_name=_('Документ'),
#                             help_text=_('Документ, в табличной части, которого данное место'),
#                             related_name='waybill_freight_packing'
#                             )
#
#     class Meta:
#         db_table = 'waybill_freight_packing'
#         verbose_name = _('Идентифицированное место в ТТН')
#         verbose_name_plural = _('Идентифицированные места в ТТН')
#         unique_together = ('doc', 'fp_type', 'row_number')
#
#     @classmethod
#     def table_fields(cls, *args, **kwargs):
#         return 'fp_type',
#
#     @classmethod
#     def form_edit_fields(cls):
#         return 'fp_type',


class WayBillStatus(BaseModel):
    """Статусы документ ТТН в разные промеутки времени, на различных этапах бизнес-процесса
    Статус может менять только проведенный документ.  document.status == PROCESSED"""
    WB_ACCEPTED = 'WB_AD'
    FP_ACCEPTED = 'FP_AD'
    FP_CHECKED = 'FP_CD'
    FP_PRODUCT_WAITING_CHECKING = 'PR_WC'
    FP_PRODUCT_CHECKED = 'PR_CD'
    READY_FOR_SHIP = 'RD_SH'

    STATUS = (
        (WB_ACCEPTED, _('ТТН проведена в системе')),
        (FP_ACCEPTED, _('Приняты места (не проверены)')),
        (FP_CHECKED, _('Места проверены и обмеряны')),
        (FP_PRODUCT_WAITING_CHECKING, _('Ожидается проверка товара')),
        (FP_PRODUCT_CHECKED, _('Товар проверен')),
        (READY_FOR_SHIP, _('Товар готов к отправке')),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True,
                                     verbose_name=_('Тип регистратора'))
    object_id = models.PositiveIntegerField(verbose_name=_('ID регистратора'), null=True)
    doc_reg = GenericForeignKey('content_type', 'object_id')

    # При первой разработке = Дате ТТН
    dt = models.DateTimeField(verbose_name=_('Дата регистрации'),
                              default=datetime.now,
                              help_text=_('Дата регистрации записи. Должна быть равна дате документа регистратора'))
    wb = models.ForeignKey('hellouser.WayBillDoc', on_delete=models.CASCADE, verbose_name='ТТН', null=True,
                           help_text=_('ТТН, по которой изменился статус'))
    status = models.CharField(max_length=5, choices=STATUS, default='', verbose_name=_('Статус ТТН'),
                              help_text=_('Статус ТТН - изменяется документами. '
                                          '<details>Разные документы, добавляют разные статус, один документ может '
                                          'добавлять два и более различных статуса в зависимости от условий.</details>')
                              )

    class Meta:
        db_table = 'waybill_status'
        verbose_name = _('Статус ТТН')
        verbose_name_plural = _('Статусы ТТН')

    @classmethod
    def table_fields(cls, *args, **kwargs):
        return 'dt', 'wb', 'doc_reg_column', 'status', 'desc'

    @classmethod
    def form_edit_fields(cls):
        return 'dt', 'wb', 'status', 'desc', 'content_type', 'object_id'


class Config(BaseModel):
    """
    Базовые настройки по умолчанию для организации, такие как: валюта, страна,
    основной покупатель, основной поставщик.
    """
    hellouser_company = models.ForeignKey('hellouser.Company', default=None, null=True, on_delete=models.SET_NULL,
                                          related_name='%(app_label)s_%(class)s_hellouser_company',
                                          verbose_name=_('Основное предприятие'))

    hellouser_currency = models.ForeignKey('hellouser.Currency', default=None, null=True, on_delete=models.SET_NULL,
                                           related_name='%(app_label)s_%(class)s_hellouser_currency',
                                           verbose_name=_('Основная валюта'))
    national_currency = models.ForeignKey('hellouser.Currency', default=None, null=True, on_delete=models.SET_NULL,
                                          related_name='%(app_label)s_%(class)s_national_currency',
                                          verbose_name=_('Национальная валюта'))
    unit_default = models.ForeignKey(
        'hellouser.Unit',
        default=None,
        null=True,
        related_name='%(app_label)s_%(class)s_hellouser_unit',
        on_delete=models.SET_NULL,
        verbose_name=_('Единица изменения по умолчанию')
    )

    class Meta:
        db_table = 'config'
        verbose_name = _('Конфигурация')
        verbose_name_plural = _('Конфигурации')
