from django.db import models

class Customer(models.Model):
    name = models.CharField('ФИО', max_length=255)
    phone = models.CharField('Телефон', max_length=20)

    def __str__(self):
        return f"{self.name} ({self.phone})"

class Car(models.Model):
    customer = models.ForeignKey(  # Добавлено поле для связи
        Customer,
        on_delete=models.CASCADE,
        related_name='cars',
        verbose_name='Владелец'
    )
    make = models.CharField('Марка', max_length=100)
    model = models.CharField('Модель', max_length=100)
    year = models.PositiveIntegerField('Год выпуска')
    vin = models.CharField('VIN', max_length=17, unique=True)

    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.vin})"


class Driver(models.Model):
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='driver',
        verbose_name='Пользователь',
        null=True,
        blank=True
    )
    name = models.CharField('ФИО', max_length=255)
    phone = models.CharField('Телефон', max_length=20)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'

    def __str__(self):
        return self.name