from django.views.generic import TemplateView
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Dealer, DealerStockNorm, DealerDistributionReport, Part
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
import os


class DealerDistributionView(TemplateView):
    template_name = 'dealers/dealer_distribution.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем всех активных дилеров
        dealers = Dealer.objects.filter(is_active=True).prefetch_related('stock_norms')

        # Получаем все детали, для которых есть нормы у дилеров
        part_ids = DealerStockNorm.objects.values_list('part_id', flat=True).distinct()
        parts = Part.objects.filter(id__in=part_ids).prefetch_related('dealer_norms')

        # Собираем данные для отчета
        report_data = []
        for part in parts:
            part_data = {
                'part': part,
                'dealers': [],
                'total_stock': 100  # Заглушка: реальный остаток на главном складе
            }

            for dealer in dealers:
                try:
                    norm = dealer.stock_norms.get(part=part)
                    current_stock = norm.current_stock if hasattr(norm, 'current_stock') else 0
                    demand = max(0, norm.norm - current_stock)
                    quantity_to_send = min(demand, part_data['total_stock'])
                    part_data['total_stock'] -= quantity_to_send

                    part_data['dealers'].append({
                        'dealer': dealer,
                        'norm': norm,
                        'demand': demand,
                        'quantity_to_send': quantity_to_send
                    })
                except DealerStockNorm.DoesNotExist:
                    part_data['dealers'].append({
                        'dealer': dealer,
                        'norm': None,
                        'demand': 0,
                        'quantity_to_send': 0
                    })

            report_data.append(part_data)

        context['report_data'] = report_data
        context['dealers'] = dealers
        return context

    def post(self, request, *args, **kwargs):
        # Сохраняем отчет в базе данных
        report = DealerDistributionReport.objects.create()

        # Создаем Excel-файл
        wb = Workbook()
        ws = wb.active
        ws.title = "Распределение"

        # Заголовки
        headers = ['Артикул', 'Наименование товара', 'Общий остаток']
        dealers = Dealer.objects.filter(is_active=True)
        for dealer in dealers:
            headers.extend([f"{dealer.customer.name} (спрос)", f"{dealer.customer.name} (отправка)"])

        ws.append(headers)

        # Стили для заголовков
        for col in range(1, len(headers) + 1):
            ws.cell(row=1, column=col).font = Font(bold=True)
            ws.cell(row=1, column=col).alignment = Alignment(horizontal='center')

        # Заполняем данными
        context = self.get_context_data()
        for item in context['report_data']:
            row = [
                item['part'].original_number,
                item['part'].name,
                item['total_stock']
            ]

            for dealer_data in item['dealers']:
                row.append(dealer_data['demand'])
                row.append(dealer_data['quantity_to_send'])

            ws.append(row)

        # Сохраняем файл
        file_name = f"dealer_distribution_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = os.path.join('media', 'dealer_reports', file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        wb.save(file_path)

        # Обновляем отчет
        report.report_file = file_path
        report.save()

        messages.success(request, 'Отчет успешно сгенерирован!')
        return redirect(reverse('admin:dealers_dealerdistributionreport_changelist'))