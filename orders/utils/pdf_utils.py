import zipfile
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics


pdfmetrics.registerFont(TTFont('Helvetica', 'fonts/Helvetica.ttf', 'utf-8'))
pdfmetrics.registerFont(TTFont('Helvetica-Bold', 'fonts/Helvetica-Bold.ttf', 'utf-8'))


def generate_delivery_map_pdf(delivery_map):
    """Генерирует PDF для карты доставки"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Настройки стилей
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        alignment=1
    )
    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontSize=9,
        leading=12
    )

    # Заголовок
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(A4[0] / 2, A4[1] - 2 * cm, "Карта доставки")

    # Информация о заказе
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, A4[1] - 3 * cm, f"Номер заказа: #{delivery_map.customer_order.id}")
    c.drawString(2 * cm, A4[1] - 3.5 * cm, f"Дата: {delivery_map.created_at.strftime('%d.%m.%Y %H:%M')}")
    c.drawString(2 * cm, A4[1] - 4 * cm, f"Покупатель: {delivery_map.customer_order.customer.name}")
    c.drawString(2 * cm, A4[1] - 4.5 * cm, f"Телефон: {delivery_map.customer_order.customer.phone}")
    c.drawString(2 * cm, A4[1] - 5 * cm, f"Автомобиль: {delivery_map.customer_order.car}")

    # Таблица с деталями
    data = []
    # Заголовки таблицы
    headers = [
        "№",
        "Деталь",
        "Кол-во",
        "Производитель",
        "Срок доставки",
        "Цена за ед.",
        "Выбор"
    ]
    data.append([Paragraph(header, header_style) for header in headers])

    # Добавляем позиции
    for i, item in enumerate(delivery_map.items.all(), 1):
        row = [
            Paragraph(str(i), cell_style),
            Paragraph(item.part.name, cell_style),
            Paragraph(str(item.quantity), cell_style),
            Paragraph(str(item.manufacturer), cell_style),
            Paragraph(item.delivery_range, cell_style),
            Paragraph(f"{item.final_price:.2f} руб.", cell_style),
            "□"  # Поле для отметки
        ]
        data.append(row)

    # Создаем таблицу
    table = Table(
        data,
        colWidths=[1 * cm, 5 * cm, 1.5 * cm, 3 * cm, 2.5 * cm, 2.5 * cm, 1.5 * cm],
        repeatRows=1
    )

    # Стили таблицы
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    table.setStyle(table_style)

    # Размещаем таблицу на странице
    table.wrapOn(c, A4[0] - 4 * cm, A4[1] - 6 * cm)
    table.drawOn(c, 2 * cm, 2 * cm)

    # Подпись
    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, 1.5 * cm, "Примечание: Покупатель отмечает нужные позиции галочкой в поле 'Выбор'")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer


def generate_customer_order_pdf(customer_order):
    """Генерирует PDF для заказа покупателя"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Настройки стилей
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        alignment=TA_CENTER
    )
    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontSize=9,
        leading=12
    )

    # Заголовок
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(A4[0] / 2, A4[1] - 2 * cm, "Заказ покупателя")

    # Начальная позиция Y для элементов
    y_position = A4[1] - 3 * cm

    # Информация о заказе
    c.setFont("Helvetica", 10)
    info_lines = [
        f"Номер заказа: #{customer_order.id}",
        f"Дата: {customer_order.created_at.strftime('%d.%m.%Y %H:%M')}",
        f"Покупатель: {customer_order.customer.name}",
        f"Телефон: {customer_order.customer.phone}",
        f"Автомобиль: {customer_order.car}",
        f"Статус: {customer_order.get_status_display()}"
    ]

    for line in info_lines:
        c.drawString(2 * cm, y_position, line)
        y_position -= 0.5 * cm

    # Рассчитываем срок доставки (если есть карта доставки)
    delivery_days = None
    if hasattr(customer_order, "delivery_map"):
        try:
            # Создаем список из правых границ диапазонов
            days_list = []
            for item in customer_order.delivery_map.items.filter(is_selected=True):
                dr = item.delivery_option.delivery_range
                if '-' in dr:
                    parts = dr.split('-')
                    if len(parts) == 2:
                        days_list.append(int(parts[1]))
                elif dr.isdigit():
                    days_list.append(int(dr))

            if days_list:
                delivery_days = max(days_list)
                c.drawString(2 * cm, y_position, f"Гарантированный срок доставки: {delivery_days} дней")
                y_position -= 0.5 * cm
        except (ValueError, TypeError):
            # Обработка ошибок преобразования
            pass

    # Добавляем отступ перед таблицей
    y_position -= 0.5 * cm

    # Таблица с деталями
    data = []
    # Заголовки таблицы
    headers = [
        "№",
        "Деталь",
        "Кол-во",
        "Цена",
        "Сумма"
    ]
    data.append([Paragraph(header, header_style) for header in headers])

    # Добавляем позиции
    total = 0
    selected_items = []
    if hasattr(customer_order, "delivery_map"):
        selected_items = customer_order.delivery_map.items.filter(is_selected=True)

    for i, item in enumerate(selected_items, 1):
        item_total = item.quantity * item.final_price
        total += item_total
        row = [
            Paragraph(str(i), cell_style),
            Paragraph(item.part.name, cell_style),
            Paragraph(str(item.quantity), cell_style),
            Paragraph(f"{item.final_price:.2f} руб.", cell_style),
            Paragraph(f"{item_total:.2f} руб.", cell_style)
        ]
        data.append(row)

    # Добавляем доставку
    if customer_order.delivery_required:
        total += float(customer_order.delivery_cost)
        row = [
            Paragraph(str(len(selected_items) + 1), cell_style),
            Paragraph("Доставка", cell_style),
            Paragraph("1", cell_style),
            Paragraph(f"{customer_order.delivery_cost:.2f} руб.", cell_style),
            Paragraph(f"{customer_order.delivery_cost:.2f} руб.", cell_style)
        ]
        data.append(row)

    # Итоговая строка
    data.append([
        "",
        Paragraph("Итого:", ParagraphStyle('Bold', parent=cell_style, fontSize=10)),
        "",
        "",
        Paragraph(f"{total:.2f} руб.", ParagraphStyle('Bold', parent=cell_style, fontSize=10))
    ])

    # Создаем таблицу
    table = Table(
        data,
        colWidths=[1 * cm, 8 * cm, 2 * cm, 3 * cm, 3 * cm],
        repeatRows=1
    )

    # Стили таблицы
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D9D9D9')),
    ])
    table.setStyle(table_style)

    # Рассчитываем высоту таблицы (примерно 0.6 см на строку)
    table_height = len(data) * 0.6 * cm

    # Размещаем таблицу на странице
    table.wrapOn(c, A4[0] - 4 * cm, min(table_height, A4[1] - 7 * cm))

    # Позиция для таблицы (с проверкой, чтобы не вышла за пределы страницы)
    table_y = y_position - table_height - 0.5 * cm
    if table_y < 2 * cm:  # Если таблица слишком длинная
        table_y = 2 * cm  # Начинаем с нижнего края страницы
        c.showPage()  # Создаем новую страницу для подписей
        table_y = A4[1] - 2 * cm - table_height

    table.drawOn(c, 2 * cm, table_y)

    # Блок для подписей
    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, 1.5 * cm, "Предоплата: ________________ руб.")
    c.drawString(12 * cm, 1.5 * cm, "Подпись покупателя: ________________")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer


def generate_supplier_order_pdf(supplier_order):
    """Генерирует PDF для заказа поставщику"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Настройки стилей
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        alignment=TA_CENTER
    )
    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontSize=9,
        leading=12
    )

    # Заголовок
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(A4[0] / 2, A4[1] - 2 * cm, "Заказ поставщику")

    # Информация о заказе
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, A4[1] - 3 * cm, f"Номер заказа: #{supplier_order.id}")
    c.drawString(2 * cm, A4[1] - 3.5 * cm, f"Дата создания: {supplier_order.created_at.strftime('%d.%m.%Y %H:%M')}")
    if supplier_order.ordered_at:
        c.drawString(2 * cm, A4[1] - 4 * cm, f"Дата заказа: {supplier_order.ordered_at.strftime('%d.%m.%Y %H:%M')}")
    c.drawString(2 * cm, A4[1] - 4.5 * cm, f"Поставщик: {supplier_order.supplier.name}")
    c.drawString(2 * cm, A4[1] - 5 * cm, f"Статус: {supplier_order.get_status_display()}")
    c.drawString(2 * cm, A4[1] - 5.5 * cm, f"Общая стоимость: {supplier_order.total_price:.2f} руб.")

    # Таблица с деталями
    data = []
    # Заголовки таблицы
    headers = [
        "№",
        "Деталь",
        "Кол-во",
        "Цена за ед.",
        "Сумма"
    ]
    data.append([Paragraph(header, header_style) for header in headers])

    # Добавляем позиции
    for i, item in enumerate(supplier_order.items.all(), 1):
        item_total = item.quantity * item.price
        row = [
            Paragraph(str(i), cell_style),
            Paragraph(item.delivery_map_item.part.name, cell_style),
            Paragraph(str(item.quantity), cell_style),
            Paragraph(f"{item.price:.2f} руб.", cell_style),
            Paragraph(f"{item_total:.2f} руб.", cell_style)
        ]
        data.append(row)

    # Итоговая строка
    data.append([
        "",
        Paragraph("Итого:", ParagraphStyle('Bold', parent=cell_style, fontSize=10)),
        "",
        "",
        Paragraph(f"{supplier_order.total_price:.2f} руб.", ParagraphStyle('Bold', parent=cell_style, fontSize=10))
    ])

    # Создаем таблицу
    table = Table(
        data,
        colWidths=[1 * cm, 8 * cm, 2 * cm, 3 * cm, 3 * cm],
        repeatRows=1
    )

    # Стили таблицы
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D9D9D9')),
    ])
    table.setStyle(table_style)

    # Размещаем таблицу на странице
    table.wrapOn(c, A4[0] - 4 * cm, A4[1] - 6 * cm)
    table.drawOn(c, 2 * cm, 2 * cm)

    # Подпись
    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, 1.5 * cm, "Подпись ответственного: ________________")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer


def generate_driver_manifest_pdf(assignment):
    """Генерирует памятку для водителя (карту доставки)"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Заголовок
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(A4[0] / 2, A4[1] - 2 * cm, "Памятка для водителя")

    # Информация о водителе и дате
    c.setFont("Helvetica", 12)
    c.drawString(2 * cm, A4[1] - 3 * cm, f"Водитель: {assignment.driver.name}")
    c.drawString(2 * cm, A4[1] - 3.5 * cm, f"Дата: {assignment.date.strftime('%d.%m.%Y')}")
    c.drawString(2 * cm, A4[1] - 4 * cm, f"Район: {assignment.district}")

    # Таблица с заказами
    data = []
    headers = [
        "№",
        "Заказчик",
        "Адрес",
        "Телефон",
        "Номера заказов",
        "Кол-во мест",
        "Сумма к получению"
    ]
    data.append(headers)

    total_items = 0
    total_amount = 0
    for i, order in enumerate(assignment.orders.all(), 1):
        items_count = sum(item.quantity for item in order.items.all())
        order_amount = sum(
            item.quantity * item.final_price for item in order.delivery_map.items.filter(is_selected=True))

        row = [
            str(i),
            order.customer.name,
            order.delivery_address,
            order.customer.phone,
            f"#{order.id}",
            str(items_count),
            f"{order_amount + order.delivery_cost:.2f} руб."
        ]
        data.append(row)

        total_items += items_count
        total_amount += order_amount + order.delivery_cost

    # Итоговая строка
    data.append([
        "",
        "Итого:",
        "",
        "",
        "",
        str(total_items),
        f"{total_amount:.2f} руб."
    ])

    # Создаем таблицу
    table = Table(
        data,
        colWidths=[1 * cm, 4 * cm, 4 * cm, 3 * cm, 2.5 * cm, 2 * cm, 3 * cm],
        repeatRows=1
    )

    # Стили таблицы
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D9D9D9')),
    ])
    table.setStyle(table_style)

    # Размещаем таблицу
    table.wrapOn(c, A4[0] - 4 * cm, A4[1] - 5 * cm)
    table.drawOn(c, 2 * cm, 2 * cm)

    # Подпись
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, 1.5 * cm, f"Общая сумма к сдаче в кассу: {total_amount:.2f} руб.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def generate_waybill_pdf(assignment):
    """Генерирует транспортные накладные для каждого клиента"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for order in assignment.orders.all():
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)

            # Заголовок
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(A4[0] / 2, A4[1] - 2 * cm, "Транспортная накладная")

            # Информация о компании
            c.setFont("Helvetica", 10)
            c.drawString(2 * cm, A4[1] - 3 * cm, "Продавец: Магазин Автозапчастей")
            c.drawString(2 * cm, A4[1] - 3.5 * cm, "Адрес: г. Москва, ул. Автозапчастей, д.1")
            c.drawString(2 * cm, A4[1] - 4 * cm, "Телефон: +7 (495) 123-45-67")

            # Информация о клиенте
            c.drawString(2 * cm, A4[1] - 5 * cm, f"Клиент: {order.customer.name}")
            c.drawString(2 * cm, A4[1] - 5.5 * cm, f"Адрес: {order.delivery_address}")
            c.drawString(2 * cm, A4[1] - 6 * cm, f"Дата доставки: {assignment.date.strftime('%d.%m.%Y')}")
            c.drawString(2 * cm, A4[1] - 6.5 * cm,
                         f"Время: {order.delivery_time.strftime('%H:%M') if order.delivery_time else 'Любое'}")

            # Таблица с товарами
            data = []
            headers = ["№", "Наименование", "Кол-во", "Цена", "Сумма"]
            data.append(headers)

            total = 0
            for i, item in enumerate(order.items.all(), 1):
                item_total = item.quantity * item.final_price
                total += item_total
                row = [
                    str(i),
                    item.part.name,
                    str(item.quantity),
                    f"{item.final_price:.2f} руб.",
                    f"{item_total:.2f} руб."
                ]
                data.append(row)

            # Добавляем доставку
            if order.delivery_required:
                total += order.delivery_cost
                row = [
                    str(len(order.items.all()) + 1),
                    "Доставка",
                    "1",
                    f"{order.delivery_cost:.2f} руб.",
                    f"{order.delivery_cost:.2f} руб."
                ]
                data.append(row)

            # Итог
            data.append([
                "",
                "Итого:",
                "",
                "",
                f"{total:.2f} руб."
            ])

            # Создаем таблицу
            table = Table(
                data,
                colWidths=[1 * cm, 8 * cm, 2 * cm, 3 * cm, 3 * cm],
                repeatRows=1
            )

            # Стили таблицы
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D9D9D9')),
            ])
            table.setStyle(table_style)

            # Размещаем таблицу
            table.wrapOn(c, A4[0] - 4 * cm, A4[1] - 7 * cm)
            table.drawOn(c, 2 * cm, 2 * cm)

            # Подписи
            c.setFont("Helvetica", 10)
            c.drawString(2 * cm, 1.5 * cm, "Подпись водителя: ________________")
            c.drawString(10 * cm, 1.5 * cm, "Подпись клиента: ________________")

            c.showPage()
            c.save()
            buffer.seek(0)
            zip_file.writestr(f"waybill_{order.id}.pdf", buffer.getvalue())

    zip_buffer.seek(0)
    return zip_buffer