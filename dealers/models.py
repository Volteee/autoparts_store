from django.db import models
from django.core.validators import MinValueValidator
from core.models import Customer
from parts.models import Part

class Dealer(models.Model):
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='dealer',
        verbose_name='Покупатель'
    )
    email = models.EmailField('Email для рассылки')
    contact_person = models.CharField('Контактное лицо', max_length=255)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)

    class Meta:
        verbose_name = 'Дилер'
        verbose_name_plural = 'Дилеры'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.name} ({self.contact_person})"

class DealerStockNorm(models.Model):
    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE,
        related_name='stock_norms',
        verbose_name='Дилер'
    )
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='dealer_norms',
        verbose_name='Запчасть'
    )
    norm = models.PositiveIntegerField('Норма запаса', default=0)
    current_stock = models.PositiveIntegerField(
        'Текущий запас',
        default=0,
        help_text='Заполняется дилером при отправке файла'
    )

    class Meta:
        verbose_name = 'Норма запаса дилера'
        verbose_name_plural = 'Нормы запасов дилеров'
        unique_together = [['dealer', 'part']]

    def __str__(self):
        return f"{self.part.name} для {self.dealer} (норма: {self.norm})"

class DealerDistributionReport(models.Model):
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    report_file = models.FileField(
        'Файл отчета',
        upload_to='dealer_reports/%Y/%m/%d/',
        null=True,
        blank=True
    )
    waybills_generated = models.BooleanField('Накладные сгенерированы', default=False)

    class Meta:
        verbose_name = 'Отчет по распределению дилерам'
        verbose_name_plural = 'Отчеты по распределению дилерам'
        ordering = ['-created_at']

    def __str__(self):
        return f"Отчет от {self.created_at.strftime('%d.%m.%Y %H:%M')}"

class DealerWaybill(models.Model):
    report = models.ForeignKey(
        DealerDistributionReport,
        on_delete=models.CASCADE,
        related_name='waybills',
        verbose_name='Отчет'
    )
    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE,
        related_name='waybills',
        verbose_name='Дилер'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    waybill_file = models.FileField(
        'Файл накладной',
        upload_to='dealer_waybills/%Y/%m/%d/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Транспортная накладная для дилера'
        verbose_name_plural = 'Транспортные накладные для дилеров'
        ordering = ['-created_at']
        unique_together = [['report', 'dealer']]

    def __str__(self):
        return f"Накладная для {self.dealer} ({self.created_at.strftime('%d.%m.%Y')})"