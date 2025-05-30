from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from .models import CustomerOrder, OrderItem, SupplierOrder, SupplierOrderItem, GoodsReceipt, GoodsReceiptItem, Supplier
from django.urls import reverse, path
from django.utils.html import format_html
from .views import CustomerOrderPDFView, DeliveryMapPDFView, SupplierOrderPDFView

import os


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['part', 'quantity', 'original_number']
    readonly_fields = ['part', 'original_number']  # Поле только для чтения
    autocomplete_fields = ['part']

    def original_number(self, obj):
        return obj.part.original_number

    original_number.short_description = 'Оригинальный номер'


@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'car',
        'phone',
        'status',
        'created_at',
        'delivery_required',
        'print_customer_order'
    )
    list_filter = ('status', 'created_at', 'delivery_required')
    search_fields = (
        'customer__name',
        'car__vin',
        'car__make',
        'car__model'
    )
    inlines = [OrderItemInline]
    fieldsets = (
        (None, {
            'fields': (
                'customer',
                'car',
                'status'
            )
        }),
        ('Сроки доставки', {
            'fields': (
                'min_delivery_time',
                'max_delivery_time'
            )
        }),
        ('Доставка', {
            'fields': (
                'delivery_required',
                'delivery_cost'
            )
        }),
    )

    def phone(self, obj):
        return obj.customer.phone

    phone.short_description = 'Телефон'

    def print_customer_order(self, obj):
        url = reverse('admin:customer_order_pdf', args=[obj.id])
        return format_html('<a class="button" href="{}">Печать заказа</a>', url)

    print_customer_order.short_description = 'Действия'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pk>/pdf/',
                self.admin_site.admin_view(CustomerOrderPDFView.as_view()),
                name='customer_order_pdf'
            ),
        ]
        return custom_urls + urls


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'part', 'quantity', 'original_number')
    search_fields = (
        'order__id',
        'part__name',
        'part__original_number'
    )
    list_filter = ('part__category', 'part__manufacturer')

    def original_number(self, obj):
        return obj.part.original_number

    original_number.short_description = 'Оригинальный номер'


from .models import DeliveryMap, DeliveryMapItem


class DeliveryMapItemInline(admin.TabularInline):
    model = DeliveryMapItem
    extra = 0
    fields = [
        'part',
        'quantity',
        'manufacturer',
        'delivery_range',
        'final_price',
        'is_selected'
    ]
    readonly_fields = fields[:-1]  # Все поля, кроме is_selected, только для чтения
    autocomplete_fields = ['part', 'delivery_option']

    def manufacturer(self, obj):
        return obj.delivery_option.part.manufacturer

    manufacturer.short_description = 'Производитель'

    def delivery_range(self, obj):
        return obj.delivery_option.get_delivery_range_display()

    delivery_range.short_description = 'Срок доставки'

    def final_price(self, obj):
        return f"{obj.final_price} руб"

    final_price.short_description = 'Цена с наценкой'


@admin.register(DeliveryMap)
class DeliveryMapAdmin(admin.ModelAdmin):
    list_display = ('customer_order', 'created_at', 'markup_percentage', 'total_price')  # Изменено customer_order
    search_fields = ('customer_order__id',)  # Обновлено
    inlines = [DeliveryMapItemInline]
    readonly_fields = ['created_at', 'total_price']

    def total_price(self, obj):
        return f"{obj.total_price()} руб"

    total_price.short_description = 'Итоговая стоимость'

    def print_delivery_map(self, obj):
        url = reverse('admin:delivery_map_pdf', args=[obj.id])
        return format_html('<a class="button" href="{}">Печать карты доставки</a>', url)

    print_delivery_map.short_description = 'Действия'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pk>/pdf/',
                self.admin_site.admin_view(DeliveryMapPDFView.as_view()),
                name='delivery_map_pdf'
            ),
        ]
        return custom_urls + urls


@admin.register(DeliveryMapItem)
class DeliveryMapItemAdmin(admin.ModelAdmin):
    list_display = (
        'delivery_map',
        'part',
        'quantity',
        'final_price',
        'delivery_range',
        'is_selected'
    )
    list_filter = ('is_selected', 'delivery_option__delivery_range')
    search_fields = ('part__name', 'delivery_map__order__id')

    def final_price(self, obj):
        return f"{obj.final_price} руб"

    final_price.short_description = 'Цена с наценкой'

    def delivery_range(self, obj):
        return obj.delivery_option.get_delivery_range_display()

    delivery_range.short_description = 'Срок доставки'


@admin.register(SupplierOrderItem)
class SupplierOrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'supplier_order',
        'part',
        'quantity',
        'price',
        'total_price'
    )
    search_fields = (
        'part__name',
        'part__original_number',
        'supplier_order__id'
    )
    list_filter = ('supplier_order__supplier',)
    autocomplete_fields = ['part', 'delivery_map_item']

    def total_price(self, obj):
        return f"{obj.quantity * obj.price:.2f} руб"

    total_price.short_description = 'Сумма'


# Теперь определяем SupplierOrderItemInline
class SupplierOrderItemInline(admin.TabularInline):
    model = SupplierOrderItem
    extra = 0
    fields = [
        'delivery_map_item',
        'part',
        'quantity',
        'price',
        'total_price'
    ]
    readonly_fields = ['total_price', 'part']
    autocomplete_fields = ['delivery_map_item', 'part']

    def total_price(self, obj):
        return f"{(obj.quantity if obj.quantity else 0) * (obj.price if obj.price else 0):.2f} руб"

    total_price.short_description = 'Сумма'


@admin.register(SupplierOrder)
class SupplierOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'supplier',
        'created_at',
        'status',
        'total_price',
        'print_supplier_order'
    )
    list_filter = ('status', 'supplier', 'created_at')
    search_fields = ('supplier__name',)
    inlines = [SupplierOrderItemInline]
    actions = ['mark_as_ordered', 'export_to_excel']

    def print_supplier_order(self, obj):
        url = reverse('admin:supplier_order_pdf', args=[obj.id])
        return format_html('<a class="button" href="{}">Печать заказа</a>', url)

    print_supplier_order.short_description = 'Действия'

    def mark_as_ordered(self, request, queryset):
        updated = queryset.filter(status='draft').update(
            status='ordered',
            ordered_at=timezone.now()
        )
        self.message_user(
            request,
            f"Помечено как 'Заказано' для {updated} заказов",
            messages.SUCCESS
        )

    mark_as_ordered.short_description = 'Пометить как заказано'

    def export_to_excel(self, request, queryset):
        # Реализация экспорта в Excel будет позже
        self.message_user(
            request,
            "Экспорт в Excel будет реализован в следующем шаге",
            messages.INFO
        )

    export_to_excel.short_description = 'Экспорт в Excel'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pk>/pdf/',
                self.admin_site.admin_view(SupplierOrderPDFView.as_view()),
                name='supplier_order_pdf'
            ),
            path(
                'generate/',
                self.admin_site.admin_view(self.generate_supplier_orders_view),
                name='generate_supplier_orders'
            ),
        ]
        return custom_urls + urls

    def generate_supplier_orders_view(self, request):
        from .utils.suppliers import generate_supplier_orders

        if request.method == 'POST':
            try:
                created_orders = generate_supplier_orders()
                if created_orders:
                    self.message_user(
                        request,
                        f"Успешно создано {len(created_orders)} заказов поставщикам",
                        messages.SUCCESS
                    )
                else:
                    self.message_user(
                        request,
                        "Нет новых выбранных позиций для создания заказов",
                        messages.INFO
                    )
            except Exception as e:
                self.message_user(
                    request,
                    f"Ошибка генерации заказов: {str(e)}",
                    messages.ERROR
                )
            return HttpResponseRedirect('../')

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
        }
        return render(
            request,
            'admin/generate_supplier_orders.html',
            context
        )

    change_list_template = 'admin/supplier_order_change_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['generate_url'] = reverse('admin:generate_supplier_orders')
        return super().changelist_view(request, extra_context=extra_context)


class GoodsReceiptItemInline(admin.TabularInline):
    model = GoodsReceiptItem
    extra = 0
    fields = ['supplier_order_item', 'quantity_received', 'price_per_unit', 'total_price']
    readonly_fields = ['price_per_unit', 'total_price']
    autocomplete_fields = ['supplier_order_item']  # Теперь должно работать

    def price_per_unit(self, obj):
        return f"{(float(obj.supplier_order_item.price) if obj.supplier_order_item.price else 0):.2f} руб"

    price_per_unit.short_description = 'Цена за ед.'

    def total_price(self, obj):
        return f"{(obj.quantity_received if obj.quantity_received else 0) * (float(obj.supplier_order_item.price) if obj.supplier_order_item.price else 0):.2f} руб"

    total_price.short_description = 'Сумма'


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'supplier_order', 'received_at', 'total_amount')
    readonly_fields = ['supplier', 'total_amount']
    search_fields = ('supplier_order__id',)
    inlines = [GoodsReceiptItemInline]

    change_form_template = 'admin/goods_receipt_change_form.html'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Обновляем статус связанного заказа
        if not change:
            obj.supplier_order.status = 'delivered'
            obj.supplier_order.save()

    def total_amount(self, obj):
        return f"{sum(item.supplier_order_item.price * item.quantity_received for item in GoodsReceiptItem.objects.all().filter(receipt=obj)):.2f} руб"

    total_amount.short_description = 'Общая сумма'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:receipt_id>/import/',
                self.admin_site.admin_view(self.import_view),
                name='import_goods_receipt'
            ),
        ]
        return custom_urls + urls

    def import_view(self, request, receipt_id=None):
        from django import forms

        class ImportForm(forms.Form):
            file = forms.FileField(label='Файл Excel')

        receipt = GoodsReceipt.objects.get(id=receipt_id)
        supplier = receipt.supplier

        if request.method == 'POST':
            form = ImportForm(request.POST, request.FILES)
            if form.is_valid():
                from django.core.management import call_command
                from django.core.files.storage import default_storage

                # Сохраняем файл
                file = request.FILES['file']
                file_name = default_storage.save(file.name, file)
                file_path = default_storage.path(file_name)

                # Запускаем импорт
                # try:
                call_command(
                    'import_goods_receipt',
                    file_path,
                    supplier.id,
                    receipt_id,
                )
                self.message_user(
                    request,
                    'Накладная успешно импортирована!',
                    messages.SUCCESS
                )
                # except Exception as e:
                #     self.message_user(
                #         request,
                #         f'Ошибка импорта: {str(e)}',
                #         messages.ERROR
                #     )
                # finally:
                #     # Удаляем временный файл
                #     if os.path.exists(file_path):
                #         os.remove(file_path)
                #
                # return HttpResponseRedirect('../')
        else:
            form = ImportForm()

        context = {
            **self.admin_site.each_context(request),
            'form': form,
            'opts': self.model._meta,
        }
        return render(
            request,
            'admin/import_goods_receipt.html',
            context
        )
