from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import PartCategory, Manufacturer, Supplier, Part, PriceList, DeliveryOption
from .forms import PartCategoryForm, ManufacturerForm, SupplierForm, PartForm, PriceListForm, DeliveryOptionForm
from core.mixins import RoleRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin

# PartCategory Views
class PartCategoryListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = PartCategory
    template_name = 'parts/category_list.html'
    context_object_name = 'categories'
    allowed_roles = ['parts_manager']

class PartCategoryCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = PartCategory
    form_class = PartCategoryForm
    template_name = 'parts/category_form.html'
    success_url = reverse_lazy('category_list')
    allowed_roles = ['parts_manager']

class PartCategoryUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = PartCategory
    form_class = PartCategoryForm
    template_name = 'parts/category_form.html'
    success_url = reverse_lazy('category_list')
    allowed_roles = ['parts_manager']

class PartCategoryDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = PartCategory
    template_name = 'parts/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')
    allowed_roles = ['parts_manager']

# Manufacturer Views
class ManufacturerListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Manufacturer
    template_name = 'parts/manufacturer_list.html'
    context_object_name = 'manufacturers'
    allowed_roles = ['parts_manager']

class ManufacturerCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Manufacturer
    form_class = ManufacturerForm
    template_name = 'parts/manufacturer_form.html'
    success_url = reverse_lazy('manufacturer_list')
    allowed_roles = ['parts_manager']

class ManufacturerUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Manufacturer
    form_class = ManufacturerForm
    template_name = 'parts/manufacturer_form.html'
    success_url = reverse_lazy('manufacturer_list')
    allowed_roles = ['parts_manager']

class ManufacturerDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Manufacturer
    template_name = 'parts/manufacturer_confirm_delete.html'
    success_url = reverse_lazy('manufacturer_list')
    allowed_roles = ['parts_manager']

# Supplier Views
class SupplierListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Supplier
    template_name = 'parts/supplier_list.html'
    context_object_name = 'suppliers'
    allowed_roles = ['supply_manager']

class SupplierCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'parts/supplier_form.html'
    success_url = reverse_lazy('supplier_list')
    allowed_roles = ['supply_manager']

class SupplierUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'parts/supplier_form.html'
    success_url = reverse_lazy('supplier_list')
    allowed_roles = ['supply_manager']

class SupplierDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'parts/supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier_list')
    allowed_roles = ['supply_manager']

# Part Views
class PartListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Part
    template_name = 'parts/part_list.html'
    context_object_name = 'parts'
    allowed_roles = ['parts_manager']

class PartCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Part
    form_class = PartForm
    template_name = 'parts/part_form.html'
    success_url = reverse_lazy('part_list')
    allowed_roles = ['parts_manager']

class PartUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Part
    form_class = PartForm
    template_name = 'parts/part_form.html'
    success_url = reverse_lazy('part_list')
    allowed_roles = ['parts_manager']

class PartDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Part
    template_name = 'parts/part_confirm_delete.html'
    success_url = reverse_lazy('part_list')
    allowed_roles = ['parts_manager']

# PriceList Views
class PriceListListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = PriceList
    template_name = 'parts/pricelist_list.html'
    context_object_name = 'price_lists'
    allowed_roles = ['supply_manager']

class PriceListCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = PriceList
    form_class = PriceListForm
    template_name = 'parts/pricelist_form.html'
    success_url = reverse_lazy('pricelist_list')
    allowed_roles = ['supply_manager']

class PriceListDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = PriceList
    template_name = 'parts/pricelist_confirm_delete.html'
    success_url = reverse_lazy('pricelist_list')
    allowed_roles = ['supply_manager']

# DeliveryOption Views
class DeliveryOptionListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = DeliveryOption
    template_name = 'parts/deliveryoption_list.html'
    context_object_name = 'options'
    allowed_roles = ['supply_manager']

class DeliveryOptionCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = DeliveryOption
    form_class = DeliveryOptionForm
    template_name = 'parts/deliveryoption_form.html'
    success_url = reverse_lazy('deliveryoption_list')
    allowed_roles = ['supply_manager']

class DeliveryOptionUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = DeliveryOption
    form_class = DeliveryOptionForm
    template_name = 'parts/deliveryoption_form.html'
    success_url = reverse_lazy('deliveryoption_list')
    allowed_roles = ['supply_manager']

class DeliveryOptionDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = DeliveryOption
    template_name = 'parts/deliveryoption_confirm_delete.html'
    success_url = reverse_lazy('deliveryoption_list')
    allowed_roles = ['supply_manager']