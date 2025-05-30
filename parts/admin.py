from django.contrib import admin
from django.utils.html import format_html

from .models import (
    PartCategory, Manufacturer, Supplier, Part,
    PriceList, DeliveryOption
)
from django.urls import path
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import PriceList


@admin.register(PartCategory)
class PartCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_info', 'payment_report_link')
    search_fields = ('name',)

    def payment_report_link(self, obj):
        from django.urls import reverse
        url = reverse('payment_report')
        return format_html('<a href="{}">Отчет по платежам</a>', url)

    payment_report_link.short_description = 'Отчеты'

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'manufacturer', 'location')
    search_fields = ('name', 'original_number', 'synonyms')
    list_filter = ('category', 'manufacturer', 'location')

class DeliveryOptionInline(admin.TabularInline):
    model = DeliveryOption
    extra = 0
    fields = ['part', 'delivery_range', 'price', 'in_stock']
    autocomplete_fields = ['part']


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'uploaded_at', 'is_active', 'is_valid_display')
    list_filter = ('supplier', 'is_active')
    search_fields = ('supplier__name',)
    inlines = [DeliveryOptionInline]
    readonly_fields = ['is_valid_display']

    def is_valid_display(self, obj):
        return obj.is_valid

    is_valid_display.boolean = True
    is_valid_display.short_description = 'Актуален (15 дней)'
    change_form_template = 'admin/price_list_change_form.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pricelist_id>/import/',
                self.admin_site.admin_view(self.import_view),
                name='import_price_list'
            ),
        ]
        return custom_urls + urls

    def import_view(self, request, pricelist_id):
        pricelist = PriceList.objects.get(id=pricelist_id)

        if request.method == 'POST':
            from django.core.management import call_command
            try:
                call_command(
                    'import_price_list',
                    pricelist.supplier.id,
                    pricelist.file.path,
                    pricelist_id,
                )
                self.message_user(
                    request,
                    'Прайс-лист успешно импортирован!',
                    level='success'
                )
            except Exception as e:
                self.message_user(
                    request,
                    f'Ошибка импорта: {str(e)}',
                    level='error'
                )
            return HttpResponseRedirect(
                f'../../{pricelist_id}/change/'
            )

        context = {
            **self.admin_site.each_context(request),
            'pricelist': pricelist,
            'opts': self.model._meta,
        }
        return render(
            request,
            'admin/price_list_import.html',
            context
        )


@admin.register(DeliveryOption)
class DeliveryOptionAdmin(admin.ModelAdmin):
    list_display = ('part', 'price_list', 'delivery_range', 'price', 'in_stock')
    list_filter = ('delivery_range', 'price_list__supplier')
    search_fields = ('part__name', 'part__original_number')
    autocomplete_fields = ['part', 'price_list']