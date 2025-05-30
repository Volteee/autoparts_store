from ..models import SupplierOrder, SupplierOrderItem, DeliveryMapItem
from django.db import transaction
from collections import defaultdict


def generate_supplier_orders():
    """
    Генерирует заказы поставщикам на основе выбранных покупателями позиций
    """
    # Находим все выбранные позиции, еще не включенные в заказ поставщику
    selected_items = DeliveryMapItem.objects.filter(
        is_selected=True,
        supplier_order_items__isnull=True
    ).select_related(
        'delivery_option__price_list__supplier'
    )

    if not selected_items:
        return None

    # Группируем позиции по поставщику
    supplier_items = defaultdict(list)
    for item in selected_items:
        supplier = item.delivery_option.price_list.supplier
        supplier_items[supplier].append(item)

    # Создаем заказы для каждого поставщика
    created_orders = []
    with transaction.atomic():
        for supplier, items in supplier_items.items():
            # Создаем заказ поставщику
            supplier_order = SupplierOrder.objects.create(
                supplier=supplier,
                status='draft'
            )

            # Добавляем позиции в заказ
            for item in items:
                # Создаем позицию заказа поставщику
                supplier_order_item = SupplierOrderItem.objects.create(
                    supplier_order=supplier_order,
                    part=item.part,  # Используем прямое поле part
                    quantity=item.quantity,
                    price=item.delivery_option.price,  # Цена без наценки
                    delivery_map_item=item  # Связь с DeliveryMapItem
                )

                # Обновляем связь в DeliveryMapItem через обратную связь
                # Теперь это делается автоматически через ForeignKey

            created_orders.append(supplier_order)

    return created_orders