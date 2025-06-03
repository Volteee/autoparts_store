from django import forms
from .models import (
    CustomerOrder, OrderItem, DeliveryMap, DeliveryMapItem,
    SupplierOrder, SupplierOrderItem, GoodsReceipt, GoodsReceiptItem,
    SupplierPayment, DriverAssignment
)

class CustomerOrderForm(forms.ModelForm):
    class Meta:
        model = CustomerOrder
        fields = [
            'customer', 'car', 'min_delivery_time', 'max_delivery_time',
            'delivery_required', 'delivery_address', 'delivery_district',
            'delivery_time', 'status'
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'car': forms.Select(attrs={'class': 'form-select'}),
            'delivery_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['part', 'quantity']
        widgets = {
            'part': forms.Select(attrs={'class': 'form-select'}),
        }

class DeliveryMapForm(forms.ModelForm):
    class Meta:
        model = DeliveryMap
        fields = ['markup_percentage']

class DeliveryMapItemForm(forms.ModelForm):
    class Meta:
        model = DeliveryMapItem
        fields = ['delivery_option', 'quantity', 'is_selected']
        widgets = {
            'delivery_option': forms.Select(attrs={'class': 'form-select'}),
        }

class SupplierOrderForm(forms.ModelForm):
    class Meta:
        model = SupplierOrder
        fields = ['supplier', 'status']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class SupplierOrderItemForm(forms.ModelForm):
    class Meta:
        model = SupplierOrderItem
        fields = ['part', 'quantity', 'price', 'delivery_map_item']
        widgets = {
            'part': forms.Select(attrs={'class': 'form-select'}),
            'delivery_map_item': forms.Select(attrs={'class': 'form-select'}),
        }

class GoodsReceiptForm(forms.ModelForm):
    class Meta:
        model = GoodsReceipt
        fields = ['supplier_order', 'notes']
        widgets = {
            'supplier_order': forms.Select(attrs={'class': 'form-select'}),
        }

class GoodsReceiptItemForm(forms.ModelForm):
    class Meta:
        model = GoodsReceiptItem
        fields = ['supplier_order_item', 'part', 'quantity_received', 'price']
        widgets = {
            'supplier_order_item': forms.Select(attrs={'class': 'form-select'}),
            'part': forms.Select(attrs={'class': 'form-select'}),
        }

class SupplierPaymentForm(forms.ModelForm):
    class Meta:
        model = SupplierPayment
        fields = ['supplier', 'month', 'amount', 'is_prepayment']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.DateInput(attrs={'type': 'month'}),
        }

class DriverAssignmentForm(forms.ModelForm):
    class Meta:
        model = DriverAssignment
        fields = ['driver', 'date', 'district', 'orders']
        widgets = {
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'orders': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }