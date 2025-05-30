def menu_items(request):
    items = []
    if request.user.is_authenticated:
        if request.user.role == 'operator':
            items.append({'url': '/orders/create/', 'title': 'Создать заказ'})
            items.append({'url': '/orders/', 'title': 'Мои заказы'})

        if request.user.role == 'parts_manager':
            items.append({'url': '/orders/process/', 'title': 'Обработка заказов'})
            items.append({'url': '/parts/', 'title': 'Каталог деталей'})

        if request.user.role == 'supply_manager':
            items.append({'url': '/suppliers/orders/', 'title': 'Заказы поставщикам'})
            items.append({'url': '/suppliers/reports/', 'title': 'Отчеты по платежам'})

        if request.user.role == 'storekeeper':
            items.append({'url': '/warehouse/receipts/', 'title': 'Приходные накладные'})
            items.append({'url': '/warehouse/inventory/', 'title': 'Инвентаризация'})

        if request.user.role == 'delivery_manager':
            items.append({'url': '/delivery/schedule/', 'title': 'График доставок'})
            items.append({'url': '/delivery/reports/', 'title': 'Отчеты по доставкам'})

    return {'menu_items': items}