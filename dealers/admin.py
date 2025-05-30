from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
from django.contrib import messages
from .models import Dealer, DealerStockNorm, DealerDistributionReport, DealerWaybill
from .utils import generate_dealer_report_excel, generate_dealer_waybill_pdf
import os
from django.conf import settings


class DealerStockNormInline(admin.TabularInline):
    model = DealerStockNorm
    extra = 0
    fields = ['part', 'norm', 'current_stock']
    autocomplete_fields = ['part']


@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ('customer', 'contact_person', 'email', 'is_active', 'created_at', 'distribution_link')
    search_fields = ('customer__name', 'contact_person', 'email')
    list_filter = ('is_active', 'created_at')
    inlines = [DealerStockNormInline]
    readonly_fields = ('created_at',)

    def distribution_link(self, obj):
        url = reverse('admin:dealer_distribution_report')
        return format_html('<a href="{}">Распределение товаров</a>', url)

    distribution_link.short_description = 'Действия'


@admin.register(DealerStockNorm)
class DealerStockNormAdmin(admin.ModelAdmin):
    list_display = ('dealer', 'part', 'norm', 'current_stock')
    search_fields = ('dealer__customer__name', 'part__name', 'part__original_number')
    list_filter = ('dealer',)
    autocomplete_fields = ['dealer', 'part']


class DealerWaybillInline(admin.TabularInline):
    model = DealerWaybill
    extra = 0
    fields = ['dealer', 'created_at', 'download_link']
    readonly_fields = ['created_at', 'download_link']

    def download_link(self, obj):
        if obj.waybill_file:
            return format_html('<a href="{}" target="_blank">Скачать накладную</a>', obj.waybill_file.url)
        return "Не сгенерирована"

    download_link.short_description = 'Накладная'


@admin.register(DealerDistributionReport)
class DealerDistributionReportAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'download_link', 'waybills_generated', 'generate_waybills_link')
    readonly_fields = ('created_at', 'download_link', 'waybills_generated')
    inlines = [DealerWaybillInline]
    actions = ['generate_waybills_action']
    change_form_template = 'admin/dealer_report_change_form.html'

    def download_link(self, obj):
        if obj.report_file:
            return format_html('<a href="{}" target="_blank">Скачать отчет</a>', obj.report_file.url)
        return "Не сгенерирован"

    download_link.short_description = 'Отчет'

    def generate_waybills_link(self, obj):
        if obj.waybills_generated:
            return "Накладные сгенерированы"
        return format_html(
            '<a href="{}">Сгенерировать накладные</a>',
            reverse('admin:generate_dealer_waybills', args=[obj.id])
        )

    generate_waybills_link.short_description = 'Действия'

    def generate_waybills_action(self, request, queryset):
        from .tasks import generate_dealer_waybills_for_report
        for report in queryset:
            if not report.waybills_generated:
                generate_dealer_waybills_for_report.delay(report.id)
        self.message_user(
            request,
            "Запущена фоновая генерация накладных для выбранных отчетов",
            messages.SUCCESS
        )

    generate_waybills_action.short_description = 'Сгенерировать накладные'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'distribution/',
                self.admin_site.admin_view(self.distribution_view),
                name='dealer_distribution_report'
            ),
            path(
                '<int:report_id>/generate-waybills/',
                self.admin_site.admin_view(self.generate_waybills_view),
                name='generate_dealer_waybills'
            ),
        ]
        return custom_urls + urls

    def distribution_view(self, request):
        from .forms import DealerDistributionForm
        from .tasks import process_dealer_distribution

        if request.method == 'POST':
            form = DealerDistributionForm(request.POST)
            if form.is_valid():
                # Сохраняем отчет
                report = DealerDistributionReport.objects.create()

                # Запускаем фоновую задачу
                process_dealer_distribution.delay(
                    report.id,
                    form.cleaned_data['include_inactive']
                )

                messages.success(
                    request,
                    "Запущено формирование отчета распределения. "
                    "Обновите страницу через несколько минут."
                )
                return redirect(reverse('admin:dealers_dealerdistributionreport_changelist'))
        else:
            form = DealerDistributionForm()

        context = {
            **self.admin_site.each_context(request),
            'form': form,
            'title': 'Распределение товаров для дилеров',
            'opts': self.model._meta,
        }
        return render(request, 'admin/dealer_distribution.html', context)

    def generate_waybills_view(self, request, report_id):
        report = get_object_or_404(DealerDistributionReport, id=report_id)

        if not report.report_file:
            messages.error(request, "Сначала сгенерируйте отчет распределения")
            return redirect(reverse('admin:dealers_dealerdistributionreport_changelist'))

        from .tasks import generate_dealer_waybills_for_report
        generate_dealer_waybills_for_report.delay(report.id)

        messages.success(
            request,
            "Запущена фоновая генерация транспортных накладных. "
            "Обновите страницу через несколько минут."
        )
        return redirect(reverse('admin:dealers_dealerdistributionreport_change', args=[report_id]))