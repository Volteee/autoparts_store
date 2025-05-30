from django.db import models
import os
from django.utils import timezone
from datetime import timedelta


class PartCategory(models.Model):
    name = models.CharField('Название категории', max_length=100, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительская категория'
    )

    class Meta:
        verbose_name = 'Категория запчастей'
        verbose_name_plural = 'Категории запчастей'

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField('Название производителя', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField('Название поставщика', max_length=100, unique=True)
    contact_info = models.TextField('Контактная информация', blank=True)

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

    def __str__(self):
        return self.name


class Part(models.Model):
    LOCATION_CHOICES = [
        ('left', 'Левый'),
        ('right', 'Правый'),
        ('front', 'Передний'),
        ('rear', 'Задний'),
        ('1', '1-й'),
        ('2', '2-й'),
        ('3', '3-й'),
        ('4', '4-й'),
    ]

    category = models.ForeignKey(
        PartCategory,
        on_delete=models.CASCADE,
        related_name='parts',
        verbose_name='Категория'
    )
    name = models.CharField('Название детали', max_length=200)
    original_number = models.CharField('Оригинальный номер', max_length=50, blank=True)
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        related_name='parts',
        verbose_name='Производитель'
    )
    location = models.CharField(
        'Расположение',
        max_length=20,
        choices=LOCATION_CHOICES,
        blank=True
    )
    description = models.TextField('Описание', blank=True)
    synonyms = models.TextField(
        'Синонимы/Сленговые названия',
        blank=True,
        help_text='Разделяйте названия запятыми'
    )

    class Meta:
        verbose_name = 'Запчасть'
        verbose_name_plural = 'Запчасти'
        unique_together = [['name', 'manufacturer', 'location']]

    def __str__(self):
        loc = dict(self.LOCATION_CHOICES).get(self.location, '')
        return f"{self.name} ({self.manufacturer}) {loc}".strip()


def price_list_upload_path(instance, filename):
    """Генерация пути для сохранения файлов прайс-листов"""
    date_str = timezone.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(
        'price_lists',
        f'supplier_{instance.supplier.id}',
        f'{date_str}_{filename}'
    )


class PriceList(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='price_lists',
        verbose_name='Поставщик'
    )
    file = models.FileField(
        'Файл прайс-листа',
        upload_to=price_list_upload_path
    )
    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)
    is_active = models.BooleanField('Актуален', default=True)

    class Meta:
        verbose_name = 'Прайс-лист'
        verbose_name_plural = 'Прайс-листы'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Прайс-лист {self.supplier} от {self.uploaded_at.strftime('%d.%m.%Y')}"

    @property
    def is_valid(self):
        """Проверка актуальности прайс-листа (15 дней)"""
        if not self.uploaded_at:  # Проверка на None
            return False
        return (timezone.now() - self.uploaded_at) < timedelta(days=15)


class DeliveryOption(models.Model):
    DELIVERY_RANGE_CHOICES = [
        ('3-5', '3-5 дней'),
        ('6-10', '6-10 дней'),
        ('10-20', '10-20 дней'),
    ]

    price_list = models.ForeignKey(
        PriceList,
        on_delete=models.CASCADE,
        related_name='delivery_options',
        verbose_name='Прайс-лист'
    )
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='delivery_options',
        verbose_name='Деталь'
    )
    delivery_range = models.CharField(
        'Срок доставки',
        max_length=10,
        choices=DELIVERY_RANGE_CHOICES
    )
    price = models.DecimalField(
        'Цена с доставкой',
        max_digits=10,
        decimal_places=2
    )
    in_stock = models.PositiveIntegerField('Количество на складе', default=0)

    class Meta:
        verbose_name = 'Вариант поставки'
        verbose_name_plural = 'Варианты поставки'
        unique_together = [['price_list', 'part', 'delivery_range']]

    def __str__(self):
        return (f"{self.part} от {self.price_list.supplier} "
                f"({self.get_delivery_range_display()}): {self.price} руб")