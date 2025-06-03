from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, FormView, DetailView
from .models import Customer, Car, Driver
from .forms import CustomerForm, CarForm, DriverForm, DriverUserAssignmentForm
from core.mixins import RoleRequiredMixin

class CustomerCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ['operator', 'storekeeper']
    model = Customer
    form_class = CustomerForm
    template_name = 'core/customer_form.html'
    success_url = '/core/customers/'

class CustomerUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ['operator', 'storekeeper']
    model = Customer
    form_class = CustomerForm
    template_name = 'core/customer_form.html'
    success_url = '/core/customers/'

class CarCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ['operator']
    model = Car
    form_class = CarForm
    template_name = 'core/car_form.html'
    success_url = '/core/cars/'


class DriverListView(RoleRequiredMixin, ListView):
    allowed_roles = ['delivery_manager']
    model = Driver
    template_name = 'core/driver_list.html'
    context_object_name = 'drivers'

class DriverUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ['delivery_manager']
    model = Driver
    form_class = DriverForm
    template_name = 'core/driver_form.html'

    def get_success_url(self):
        return reverse('/core/driver_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Данные водителя {self.object.name} обновлены')
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_role'] = 'driver'
        return kwargs


class CustomerListView(RoleRequiredMixin, ListView):
    allowed_roles = ['operator', 'storekeeper', 'supply_manager']
    model = Customer
    template_name = 'core/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Фильтрация по имени
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class CarUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ['operator', 'parts_manager']
    model = Car
    form_class = CarForm
    template_name = 'core/car_form.html'

    def get_success_url(self):
        return reverse('car_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Автомобиль {self.object} успешно обновлен')
        return response


class CarListView(RoleRequiredMixin, ListView):
    allowed_roles = ['operator', 'parts_manager', 'delivery_manager']
    model = Car
    template_name = 'core/car_list.html'
    context_object_name = 'cars'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Фильтрация по марке, модели или VIN
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(make__icontains=search_query) |
                models.Q(model__icontains=search_query) |
                models.Q(vin__icontains=search_query)
            )

        # Фильтрация по клиенту
        customer_id = self.request.GET.get('customer')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        return queryset.select_related('customer').order_by('make', 'model')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['customers'] = Customer.objects.all().order_by('name')
        context['selected_customer'] = self.request.GET.get('customer')
        return context


class DriverCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ['delivery_manager']
    model = Driver
    form_class = DriverForm
    template_name = 'core/driver_form.html'

    def get_success_url(self):
        return reverse('/core/driver_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Водитель {self.object.name} успешно создан')
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_role'] = 'driver'  # Передаем роль для фильтрации пользователей
        return kwargs


class DriverUserAssignmentView(RoleRequiredMixin, FormView):
    allowed_roles = ['delivery_manager']
    form_class = DriverUserAssignmentForm
    template_name = 'core/driver_assign_user.html'
    success_url = reverse_lazy('/core/driver_list')

    def form_valid(self, form):
        driver = form.cleaned_data['driver']
        user = form.cleaned_data['user']

        # Привязываем пользователя к водителю
        driver.user = user
        driver.save()

        # Обновляем роль пользователя
        user.role = 'driver'
        user.save()

        messages.success(self.request, f'Пользователь {user.username} привязан к водителю {driver.name}')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unassigned_drivers'] = Driver.objects.filter(user__isnull=True)
        context['available_users'] = get_user_model().objects.filter(
            role='driver',
            driver__isnull=True
        )
        return context


class CustomerDetailView(RoleRequiredMixin, DetailView):
    allowed_roles = ['operator', 'storekeeper', 'supply_manager']
    model = Customer
    template_name = 'core/customer_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cars'] = self.object.cars.all()
        return context


class CarDetailView(RoleRequiredMixin, DetailView):
    allowed_roles = ['operator', 'parts_manager', 'delivery_manager']
    model = Car
    template_name = 'core/car_detail.html'


class DriverDetailView(RoleRequiredMixin, DetailView):
    allowed_roles = ['delivery_manager']
    model = Driver
    template_name = 'core/driver_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment_history'] = self.object.delivery_assignments.all().order_by('-delivery_date')
        return context


