from django import forms
from .models import PartCategory, Manufacturer, Supplier, Part, PriceList, DeliveryOption

class PartCategoryForm(forms.ModelForm):
    class Meta:
        model = PartCategory
        fields = ['name', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }

class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_info']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['category', 'name', 'original_number', 'manufacturer', 'location', 'description', 'synonyms']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'original_number': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'synonyms': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class PriceListForm(forms.ModelForm):
    class Meta:
        model = PriceList
        fields = ['supplier', 'file']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
        }

class DeliveryOptionForm(forms.ModelForm):
    class Meta:
        model = DeliveryOption
        fields = ['price_list', 'part', 'delivery_range', 'price', 'in_stock']
        widgets = {
            'price_list': forms.Select(attrs={'class': 'form-select'}),
            'part': forms.Select(attrs={'class': 'form-select'}),
            'delivery_range': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'in_stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }