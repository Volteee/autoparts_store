import zipfile
from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from .models import DeliveryMap, CustomerOrder, SupplierOrder
from .utils.pdf_utils import generate_delivery_map_pdf, generate_customer_order_pdf, generate_supplier_order_pdf
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import (
    CustomerOrder, OrderItem, DeliveryMap, DeliveryMapItem,
    SupplierOrder, SupplierOrderItem, GoodsReceipt, GoodsReceiptItem,
    SupplierPayment, DriverAssignment
)
from .forms import (
    CustomerOrderForm, OrderItemForm, DeliveryMapForm, DeliveryMapItemForm,
    SupplierOrderForm, SupplierOrderItemForm, GoodsReceiptForm, GoodsReceiptItemForm,
    SupplierPaymentForm, DriverAssignmentForm
)
from core.mixins import RoleRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class DeliveryMapPDFView(View):
    def get(self, request, *args, **kwargs):
        delivery_map_id = kwargs.get('pk')
        try:
            delivery_map = DeliveryMap.objects.get(pk=delivery_map_id)
        except DeliveryMap.DoesNotExist:
            return HttpResponse("Карта доставки не найдена", status=404)

        pdf_buffer = generate_delivery_map_pdf(delivery_map)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="delivery_map_{delivery_map.id}.pdf"'
        return response


class CustomerOrderPDFView(View):
    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        try:
            customer_order = CustomerOrder.objects.get(pk=order_id)
        except CustomerOrder.DoesNotExist:
            return HttpResponse("Заказ не найден", status=404)

        pdf_buffer = generate_customer_order_pdf(customer_order)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="customer_order_{customer_order.id}.pdf"'
        return response


class SupplierOrderPDFView(View):
    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        try:
            supplier_order = SupplierOrder.objects.get(pk=order_id)
        except SupplierOrder.DoesNotExist:
            return HttpResponse("Заказ поставщику не найден", status=404)

        pdf_buffer = generate_supplier_order_pdf(supplier_order)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="supplier_order_{supplier_order.id}.pdf"'
        return response


from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Sum
from .models import GoodsReceipt, SupplierPayment, Supplier
from datetime import timedelta


class PaymentReportView(TemplateView):
    template_name = 'orders/payment_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Определяем даты для текущего и предыдущего месяцев
        today = timezone.now().date()
        current_month_start = today.replace(day=1)
        prev_month_start = (current_month_start - timedelta(days=1)).replace(day=1)

        # Получаем приходы за текущий месяц
        current_month_receipts = GoodsReceipt.objects.filter(
            received_at__gte=current_month_start,
            received_at__lt=current_month_start + timedelta(days=32)
        ).values('supplier_order__supplier').annotate(
            total_amount=Sum('total_amount')
        )

        # Получаем приходы за предыдущий месяц
        prev_month_receipts = GoodsReceipt.objects.filter(
            received_at__gte=prev_month_start,
            received_at__lt=current_month_start
        ).values('supplier_order__supplier').annotate(
            total_amount=Sum('total_amount')
        )

        # Создаем словари для быстрого доступа
        current_month_dict = {item['supplier_order__supplier']: item['total_amount'] for item in current_month_receipts}
        prev_month_dict = {item['supplier_order__supplier']: item['total_amount'] for item in prev_month_receipts}

        # Собираем данные по всем поставщикам
        suppliers = Supplier.objects.all()
        report_data = []

        for supplier in suppliers:
            current_total = current_month_dict.get(supplier.id, 0) if current_month_dict.get(supplier.id, 0) else 0
            prev_total = prev_month_dict.get(supplier.id, 0) if prev_month_dict.get(supplier.id, 0) else 0

            # Расчет рекомендованной предоплаты
            difference = current_total - prev_total
            recommended = float(current_total) + 0.5 * float(difference)

            report_data.append({
                'supplier': supplier,
                'current_month': current_total,
                'prev_month': prev_total,
                'recommended': recommended if recommended > 0 else 0
            })

        context['report_data'] = report_data
        context['current_month'] = current_month_start.strftime('%B %Y')
        context['prev_month'] = prev_month_start.strftime('%B %Y')

        return context


from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import DriverAssignment, CustomerOrder
from core.models import Driver
from .utils.pdf_utils import generate_driver_manifest_pdf, generate_waybill_pdf

from django.template.defaulttags import register
from .templatetags.custom_tags import get_item

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


class DeliveryOrdersListView(ListView):
    model = CustomerOrder
    template_name = 'orders/delivery_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # Заказы, которые готовы к доставке (оприходованы и не доставлены)
        return CustomerOrder.objects.filter(
            status='completed',
            is_delivered=False,
            delivery_required=True
        ).select_related('customer', 'car')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Группируем заказы по районам
        districts = {}
        for order in context['orders']:
            if order.delivery_district:
                if order.delivery_district not in districts:
                    districts[order.delivery_district] = []
                districts[order.delivery_district].append(order)

        # Получаем существующие назначения
        assignments = DriverAssignment.objects.filter(date=timezone.now().date())
        district_assignments = {a.district: a for a in assignments}

        context['districts'] = districts
        context['driver_assignments'] = district_assignments
        context['drivers'] = Driver.objects.filter(is_active=True)
        context['today'] = timezone.now().date()

        return context

    def post(self, request, *args, **kwargs):
        district = request.POST.get('assign')
        driver_id = request.POST.get(f'driver_{district}')

        if not driver_id:
            messages.error(request, 'Выберите водителя для назначения')
            return self.get(request, *args, **kwargs)

        driver = get_object_or_404(Driver, id=driver_id)
        orders_in_district = CustomerOrder.objects.filter(
            delivery_district=district,
            status='completed',
            is_delivered=False,
            delivery_required=True
        )

        assignment, created = DriverAssignment.objects.get_or_create(
            driver=driver,
            date=timezone.now().date(),
            district=district,
            defaults={}
        )
        assignment.orders.set(orders_in_district)

        messages.success(request, f'Водитель {driver.name} назначен на район {district}')
        return redirect('delivery_orders')


class DriverAssignmentUpdateView(UpdateView):
    model = DriverAssignment
    fields = ['driver']
    template_name = 'orders/driver_assignment.html'
    success_url = reverse_lazy('delivery_orders')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Водитель успешно назначен!')
        return response


def generate_delivery_documents(request, assignment_id):
    assignment = get_object_or_404(DriverAssignment, id=assignment_id)

    # Генерируем документы
    manifest_buffer = generate_driver_manifest_pdf(assignment)
    waybill_buffer = generate_waybill_pdf(assignment)

    # Создаем zip-архив с документами
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(f"manifest_{assignment_id}.pdf", manifest_buffer.getvalue())
        zip_file.writestr(f"waybills_{assignment_id}.zip", waybill_buffer.getvalue())

    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="delivery_docs_{assignment_id}.zip"'
    return response


def mark_as_delivered(request, assignment_id):
    assignment = get_object_or_404(DriverAssignment, id=assignment_id)

    # Помечаем заказы как доставленные
    for order in assignment.orders.all():
        order.is_delivered = True
        order.save()

    messages.success(request, f"{assignment.orders.count()} заказов помечено как доставленные!")
    return redirect('delivery_orders')


# CustomerOrder Views
class CustomerOrderListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = CustomerOrder
    template_name = 'orders/customer_order_list.html'
    context_object_name = 'orders'
    allowed_roles = ['operator', 'orders_manager', 'supply_manager']
    ordering = ['-created_at']


class CustomerOrderCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = CustomerOrder
    form_class = CustomerOrderForm
    template_name = 'orders/customer_order_form.html'
    success_url = reverse_lazy('customer_order_list')
    allowed_roles = ['operator']


class CustomerOrderUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = CustomerOrder
    form_class = CustomerOrderForm
    template_name = 'orders/customer_order_form.html'
    success_url = reverse_lazy('customer_order_list')
    allowed_roles = ['operator', 'orders_manager']


class CustomerOrderDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    model = CustomerOrder
    template_name = 'orders/customer_order_detail.html'
    allowed_roles = ['operator', 'orders_manager', 'supply_manager']
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.request.user.role in ['operator', 'orders_manager']
        return context


# OrderItem Views
class OrderItemCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/order_item_form.html'
    allowed_roles = ['operator']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = CustomerOrder.objects.get(pk=self.kwargs['order_pk'])
        return context

    def form_valid(self, form):
        order = CustomerOrder.objects.get(pk=self.kwargs['order_pk'])
        form.instance.order = order
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('customer_order_detail', kwargs={'pk': self.kwargs['order_pk']})


class OrderItemUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/order_item_form.html'
    allowed_roles = ['operator']

    def get_success_url(self):
        return reverse_lazy('customer_order_detail', kwargs={'pk': self.object.order.pk})


# DeliveryMap Views
class DeliveryMapDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    model = DeliveryMap
    template_name = 'orders/delivery_map_detail.html'
    allowed_roles = ['operator', 'parts_manager']


# DeliveryMapItem Views
class DeliveryMapItemUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = DeliveryMapItem
    form_class = DeliveryMapItemForm
    template_name = 'orders/delivery_map_item_form.html'
    allowed_roles = ['parts_manager']

    def get_success_url(self):
        return reverse_lazy('delivery_map_detail', kwargs={'pk': self.object.delivery_map.pk})


# SupplierOrder Views
class SupplierOrderListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = SupplierOrder
    template_name = 'orders/supplier_order_list.html'
    context_object_name = 'orders'
    allowed_roles = ['supply_manager']
    ordering = ['-created_at']


class SupplierOrderCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = SupplierOrder
    form_class = SupplierOrderForm
    template_name = 'orders/supplier_order_form.html'
    success_url = reverse_lazy('supplier_order_list')
    allowed_roles = ['supply_manager']


class SupplierOrderUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = SupplierOrder
    form_class = SupplierOrderForm
    template_name = 'orders/supplier_order_form.html'
    success_url = reverse_lazy('supplier_order_list')
    allowed_roles = ['supply_manager']


# GoodsReceipt Views
class GoodsReceiptListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = GoodsReceipt
    template_name = 'orders/goods_receipt_list.html'
    context_object_name = 'receipts'
    allowed_roles = ['supply_manager']
    ordering = ['-received_at']


class GoodsReceiptCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = GoodsReceipt
    form_class = GoodsReceiptForm
    template_name = 'orders/goods_receipt_form.html'
    success_url = reverse_lazy('goods_receipt_list')
    allowed_roles = ['supply_manager']


# SupplierPayment Views
class SupplierPaymentListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = SupplierPayment
    template_name = 'orders/supplier_payment_list.html'
    context_object_name = 'payments'
    allowed_roles = ['supply_manager']
    ordering = ['-month']


class SupplierPaymentCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = SupplierPayment
    form_class = SupplierPaymentForm
    template_name = 'orders/supplier_payment_form.html'
    success_url = reverse_lazy('supplier_payment_list')
    allowed_roles = ['supply_manager']


# DriverAssignment Views
class DriverAssignmentListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = DriverAssignment
    template_name = 'orders/driver_assignment_list.html'
    context_object_name = 'assignments'
    allowed_roles = ['delivery_manager']
    ordering = ['-date']


class DriverAssignmentCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = DriverAssignment
    form_class = DriverAssignmentForm
    template_name = 'orders/driver_assignment_form.html'
    success_url = reverse_lazy('driver_assignment_list')
    allowed_roles = ['delivery_manager']


class MyDriverAssignmentUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = DriverAssignment
    form_class = DriverAssignmentForm
    template_name = 'orders/driver_assignment_form.html'
    success_url = reverse_lazy('driver_assignment_list')
    allowed_roles = ['delivery_manager']