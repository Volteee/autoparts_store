from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        # Регистрируем пользовательские теги
        from . import templatetags
        from django.db.models.signals import post_save
        from .models import CustomerOrder
        from .utils.delivery_map import generate_delivery_map

        def create_delivery_map(sender, instance, created, **kwargs):
            if created and instance.status == 'processing':
                generate_delivery_map(instance)

        post_save.connect(create_delivery_map, sender=CustomerOrder)