from django.db.models import Min
from ..models import DeliveryMap, DeliveryMapItem
from parts.models import DeliveryOption


def generate_delivery_map(order):
    """
    Генерирует карту доставки для заказа
    """
    # Проверяем, нет ли уже карты для этого заказа
    if hasattr(order, 'delivery_map') and order.delivery_map is not None:
        return order.delivery_map

    # Создаем новую карту доставки
    delivery_map = DeliveryMap.objects.create(customer_order=order)

    # Для каждой позиции в заказе ищем лучшие варианты поставки
    for item in order.items.all():
        # Получаем все активные варианты поставки для этой детали
        options = DeliveryOption.objects.filter(
            part=item.part,
            price_list__is_active=True,
        ).select_related('price_list__supplier', 'part__manufacturer')

        # Группируем по производителю и сроку доставки, выбираем минимальную цену
        best_options = {}
        for option in options:
            key = (option.part.manufacturer_id, option.delivery_range)
            if key not in best_options or option.price < best_options[key].price:
                best_options[key] = option

        # Создаем позиции в карте доставки
        for option in best_options.values():
            DeliveryMapItem.objects.create(
                delivery_map=delivery_map,
                part=item.part,
                delivery_option=option,
                quantity=item.quantity
            )

    return delivery_map