from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        OPERATOR = 'operator', _('Оператор ЭВМ')
        PARTS_MANAGER = 'parts_manager', _('Менеджер по деталям')
        ORDERS_MANAGER = 'orders_manager', _('Менеджер по заказам')
        SUPPLY_MANAGER = 'supply_manager', _('Менеджер по поставкам')
        STOREKEEPER = 'storekeeper', _('Кладовщик')
        DELIVERY_MANAGER = 'delivery_manager', _('Начальник службы доставки')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.OPERATOR,
        verbose_name=_('Роль')
    )

    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Телефон'))
    address = models.TextField(blank=True, null=True, verbose_name=_('Адрес'))
    delivery_preference = models.BooleanField(
        default=False,
        verbose_name=_('Требуется доставка')
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('Группы'),
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('Права пользователя'),
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @classmethod
    def create_from_dict(cls, d):
        return cls.objects.create()