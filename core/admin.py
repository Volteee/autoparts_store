from django.contrib import admin
from .models import Customer, Car, Driver
from orders.models import CustomerOrder


class CarInline(admin.TabularInline):
    model = Car
    extra = 0
    fields = ('make', 'model', 'year', 'vin')
    readonly_fields = fields


class CustomerOrderInline(admin.TabularInline):
    model = CustomerOrder
    extra = 0
    fields = ('id', 'car', 'status', 'created_at', 'phone')
    readonly_fields = fields
    show_change_link = True

    def phone(self, obj):
        return obj.customer.phone

    phone.short_description = 'Телефон'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
    search_fields = ('name', 'phone')
    inlines = [CarInline, CustomerOrderInline]


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('customer', 'make', 'model', 'year', 'vin')
    search_fields = ('make', 'model', 'vin', 'customer__name')
    list_filter = ('customer',)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'is_active')
    search_fields = ('name', 'phone')
    list_filter = ('is_active',)