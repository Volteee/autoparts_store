from django.db import models
from django.db.models import Q

from core.models import Customer, Car
from parts.models import Part, Manufacturer, Supplier, DeliveryOption
from django.core.validators import MinValueValidator


class CustomerOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('processing', 'В обработке'),
        ('completed', 'Выполнен'),
        ('canceled', 'Отменен'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Покупатель'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Автомобиль'
    )
    min_delivery_time = models.PositiveIntegerField('Минимальный срок доставки (дни)')
    max_delivery_time = models.PositiveIntegerField('Максимальный срок доставки (дни)')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    status = models.CharField(
        'Статус заказа',
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    delivery_required = models.BooleanField(
        'Требуется доставка',
        default=False,
        help_text='Отметьте если требуется доставка курьером'
    )
    delivery_cost = models.DecimalField(
        'Стоимость доставки',
        max_digits=10,
        decimal_places=2,
        default=100.00
    )
    delivery_address = models.TextField('Адрес доставки', blank=True)
    delivery_district = models.CharField('Район доставки', max_length=100, blank=True)
    delivery_time = models.DateTimeField('Желаемое время доставки', null=True, blank=True)
    is_delivered = models.BooleanField('Доставлено', default=False)

    class Meta:
        verbose_name = 'Заказ покупателя'
        verbose_name_plural = 'Заказы покупателей'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} от {self.created_at.strftime('%d.%m.%Y')}"

    @property
    def phone(self):
        """Телефон покупателя"""
        return self.customer.phone

    def save(self, *args, **kwargs):
        # При изменении статуса на "В обработке" будет создана карта доставки
        if self.pk:
            old_status = CustomerOrder.objects.get(pk=self.pk).status
            if old_status != 'processing' and self.status == 'processing':
                super().save(*args, **kwargs)
                from .utils.delivery_map import generate_delivery_map
                generate_delivery_map(self)  # Создаем карту доставки
                return
        super().save(*args, **kwargs)

    @property
    def delivery_map(self):
        """Возвращает связанную карту доставки, если она есть."""
        try:
            return DeliveryMap.objects.get(customer_order=self)
        except DeliveryMap.DoesNotExist:
            return None


class OrderItem(models.Model):
    order = models.ForeignKey(
        CustomerOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        verbose_name='Деталь'
    )
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'
        unique_together = [['order', 'part']]

    def __str__(self):
        return f"{self.part.name} x{self.quantity}"

    @property
    def original_number(self):
        """Оригинальный номер детали"""
        return self.part.original_number


class DeliveryMap(models.Model):
    customer_order = models.OneToOneField(  # Изменено имя поля
        CustomerOrder,
        on_delete=models.CASCADE,
        related_name='delivery_map',  # Установлен related_name
        verbose_name='Заказ покупателя'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    markup_percentage = models.FloatField(
        'Наценка (%)',
        default=30,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Карта доставки'
        verbose_name_plural = 'Карты доставки'
        ordering = ['-created_at']

    def __str__(self):
        return f"Карта доставки для заказа #{self.customer_order.id}"

    def total_price(self):
        return sum(item.final_price for item in self.items.all())


class DeliveryMapItem(models.Model):
    delivery_map = models.ForeignKey(
        DeliveryMap,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Карта доставки'
    )
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        verbose_name='Деталь'
    )
    delivery_option = models.ForeignKey(
        DeliveryOption,
        on_delete=models.CASCADE,
        verbose_name='Вариант поставки'
    )
    quantity = models.PositiveIntegerField('Количество')
    is_selected = models.BooleanField('Выбрано покупателем', default=False)

    class Meta:
        verbose_name = 'Позиция карты доставки'
        verbose_name_plural = 'Позиции карты доставки'
        unique_together = [['delivery_map', 'part', 'delivery_option']]

    def __str__(self):
        return f"{self.part.name} x{self.quantity}"

    @property
    def final_price(self):
        """Цена с наценкой"""
        return round(float(self.delivery_option.price) * (1 + self.delivery_map.markup_percentage / 100), 2)

    @property
    def delivery_range(self):
        return self.delivery_option.get_delivery_range_display()

    @property
    def manufacturer(self):
        return self.delivery_option.part.manufacturer

    @property
    def supplier(self):
        return self.delivery_option.price_list.supplier


class SupplierOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('ordered', 'Заказан'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    ]

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Поставщик'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    ordered_at = models.DateTimeField('Дата заказа', null=True, blank=True)
    status = models.CharField(
        'Статус заказа',
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    total_price = models.DecimalField(
        'Общая стоимость',
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Заказ поставщику'
        verbose_name_plural = 'Заказы поставщикам'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ поставщику #{self.id} ({self.supplier.name})"

    def update_total_price(self):
        """Обновляет общую стоимость заказа"""
        self.total_price = sum(item.price * item.quantity for item in self.items.all())
        self.save()


class SupplierOrderItem(models.Model):
    supplier_order = models.ForeignKey(
        SupplierOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ поставщику'
    )
    # Убираем прямое поле связи с DeliveryMapItem
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        verbose_name='Деталь'
    )
    quantity = models.PositiveIntegerField('Количество')
    price = models.DecimalField(
        'Цена за единицу',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    delivery_map_item = models.ForeignKey(
        'DeliveryMapItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supplier_order_items',  # Уникальное имя для обратной связи
        verbose_name='Позиция карты доставки'
    )

    class Meta:
        verbose_name = 'Позиция заказа поставщику'
        verbose_name_plural = 'Позиции заказа поставщику'
        unique_together = [['supplier_order', 'part']]

    def __str__(self):
        return f"{self.part.name} x{self.quantity}"

    # Добавим метод для поиска в админке
    @classmethod
    def search(cls, term):
        return cls.objects.filter(
            Q(part__name__icontains=term) |
            Q(part__original_number__icontains=term) |
            Q(supplier_order__id__icontains=term)
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.supplier_order.update_total_price()

    def delete(self, *args, **kwargs):
        supplier_order = self.supplier_order
        super().delete(*args, **kwargs)
        supplier_order.update_total_price()


class GoodsReceiptItem(models.Model):
    receipt = models.ForeignKey(
        'GoodsReceipt',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Накладная'
    )
    supplier_order_item = models.ForeignKey(
        SupplierOrderItem,
        on_delete=models.CASCADE,
        related_name='receipt_items',  # Уникальное имя для обратной связи
        verbose_name='Позиция заказа',
        null=True,
    )
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='receipt_parts',  # Уникальное имя для обратной связи
        verbose_name='Запчасть',
        null=True,
    )
    quantity_received = models.PositiveIntegerField('Полученное количество')
    price = models.DecimalField(
        'Цена за единицу',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        null=True,
    )

    class Meta:
        verbose_name = 'Позиция приходной накладной'
        verbose_name_plural = 'Позиции приходных накладных'

    def __str__(self):
        return f"{self.part.name if self.part else self.supplier_order_item.part.name} x{self.quantity_received}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.receipt.update_total_amount()

    def delete(self, *args, **kwargs):
        receipt = self.receipt
        super().delete(*args, **kwargs)
        receipt.update_total_amount()


class GoodsReceipt(models.Model):
    supplier = models.ForeignKey(  # Добавлено поле поставщика
        Supplier,
        on_delete=models.CASCADE,
        related_name='receipts',
        verbose_name='Поставщик',
        null=True,
        blank=True
    )
    supplier_order = models.ForeignKey(
        SupplierOrder,
        on_delete=models.CASCADE,
        related_name='receipts',
        verbose_name='Заказ поставщику',
        null=True,
        blank=True
    )
    received_at = models.DateTimeField('Дата получения', auto_now_add=True)
    total_amount = models.DecimalField(
        'Общая сумма',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        null=True,
    )
    notes = models.TextField('Примечания', blank=True)

    class Meta:
        verbose_name = 'Приходная накладная'
        verbose_name_plural = 'Приходные накладные'
        ordering = ['-received_at']

    def __str__(self):
        return f"Накладная #{self.id} от {self.received_at.strftime('%d.%m.%Y')}"

    def save(self):
        self.supplier = self.supplier_order.supplier
        super().save()

    def update_total_amount(self):
        """Обновляет общую стоимость заказа"""
        items = GoodsReceiptItem.objects.all().filter(receipt=self)
        self.total_amount = sum(item.supplier_order_item.price if item.supplier_order_item else 0 * item.quantity_received for item in items)
        self.save()


class SupplierPayment(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Поставщик'
    )
    month = models.DateField('Месяц')  # Первое число месяца
    amount = models.DecimalField(
        'Сумма платежа',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    payment_date = models.DateField('Дата платежа', auto_now_add=True)
    is_prepayment = models.BooleanField('Предоплата', default=True)

    class Meta:
        verbose_name = 'Платеж поставщику'
        verbose_name_plural = 'Платежи поставщикам'
        unique_together = [['supplier', 'month']]
        ordering = ['-month']

    def __str__(self):
        return f"Платеж {self.supplier.name} за {self.month.strftime('%B %Y')}"


class DriverAssignment(models.Model):
    driver = models.ForeignKey(
        'core.Driver',
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Водитель'
    )
    date = models.DateField('Дата доставки')
    district = models.CharField('Район', max_length=100)
    orders = models.ManyToManyField(
        CustomerOrder,
        related_name='driver_assignments',
        verbose_name='Заказы',
        blank=True
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Назначение водителя'
        verbose_name_plural = 'Назначения водителей'
        unique_together = [['driver', 'date', 'district']]
        ordering = ['-date']

    def __str__(self):
        return f"{self.driver} - {self.district} ({self.date})"