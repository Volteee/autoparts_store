def menu_items(request):
    items = []
    if request.user.is_authenticated:
        # Общие пункты меню для всех ролей
        items.append({'url': '/home/', 'title': 'Главная', 'icon': 'bi-house'})

        if request.user.role == 'operator':
            # Меню для оператора
            items.append({'url': '/core/customers/', 'title': 'Клиенты', 'icon': 'bi-people'})
            items.append({'url': '/core/cars/', 'title': 'Автомобили', 'icon': 'bi-car-front'})
            items.append({'url': '/orders/customer-orders/', 'title': 'Заказы покупателей', 'icon': 'bi-cart'})

        elif request.user.role == 'parts_manager':
            # Меню для менеджера по деталям
            items.append({'url': '/parts/parts/', 'title': 'Детали', 'icon': 'bi-gear'})
            items.append({'url': '/parts/manufacturers/', 'title': 'Производители', 'icon': 'bi-building'})
            items.append({'url': '/parts/categories/', 'title': 'Категории', 'icon': 'bi-diagram-3'})
            items.append({'url': '/parts/pricelists/', 'title': 'Прайс-листы', 'icon': 'bi-currency-exchange'})

        elif request.user.role == 'orders_manager':
            # Меню для менеджера по заказам
            items.append({'url': '/orders/customer-orders/', 'title': 'Заказы покупателей', 'icon': 'bi-cart'})
            items.append({'url': '/orders/supplier-orders/', 'title': 'Заказы поставщикам', 'icon': 'bi-truck'})
            items.append({'url': '/parts/delivery-options/', 'title': 'Варианты доставки', 'icon': 'bi-clock'})

        elif request.user.role == 'supply_manager':
            # Меню для менеджера по поставкам
            items.append({'url': '/parts/suppliers/', 'title': 'Поставщики', 'icon': 'bi-box-seam'})
            items.append({'url': '/orders/supplier-orders/', 'title': 'Заказы поставщикам', 'icon': 'bi-clipboard-check'})
            items.append({'url': '/orders/goods-receipts/', 'title': 'Приходные накладные', 'icon': 'bi-clipboard-data'})
            items.append({'url': '/orders/payment-report/', 'title': 'Отчет по платежам', 'icon': 'bi-graph-up'})

        elif request.user.role == 'storekeeper':
            # Меню для кладовщика
            items.append({'url': '/orders/goods-receipts/', 'title': 'Приходные накладные', 'icon': 'bi-clipboard-check'})
            items.append({'url': '/parts/parts/', 'title': 'Складские позиции', 'icon': 'bi-boxes'})
            items.append({'url': '#', 'title': 'Печать ценников', 'icon': 'bi-printer'})
            items.append({'url': '#', 'title': 'Инвентаризация', 'icon': 'bi-clipboard'})

        elif request.user.role == 'delivery_manager':
            # Меню для начальника службы доставки
            items.append({'url': '/core/drivers/', 'title': 'Водители', 'icon': 'bi-person-badge'})
            items.append({'url': '/orders/driver-assignments/', 'title': 'Назначения', 'icon': 'bi-calendar-check'})
            items.append({'url': '#', 'title': 'Отчет по доставкам', 'icon': 'bi-graph-up'})

        elif request.user.role == 'driver':
            # Меню для водителя
            items.append({'url': '#', 'title': 'Мои доставки', 'icon': 'bi-list-task'})
            items.append({'url': '#', 'title': 'Карты доставки', 'icon': 'bi-map'})
            items.append({'url': '#', 'title': 'Маршруты', 'icon': 'bi-signpost'})

        # Общий пункт для профиля
        items.append({'url': '#', 'title': 'Профиль', 'icon': 'bi-person'})

    return {'menu_items': items}