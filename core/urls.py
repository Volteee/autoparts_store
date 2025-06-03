from django.urls import path
from .views import (
    CustomerListView, CustomerCreateView, CustomerUpdateView, CustomerDetailView,
    CarListView, CarCreateView, CarUpdateView, CarDetailView,
    DriverListView, DriverCreateView, DriverUpdateView, DriverDetailView,
    DriverUserAssignmentView
)

urlpatterns = [
    # Customer URLs
    path('customers/', CustomerListView.as_view(), name='customer_list'),
    path('customers/create/', CustomerCreateView.as_view(), name='customer_create'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/<int:pk>/edit/', CustomerUpdateView.as_view(), name='customer_update'),

    # Car URLs
    path('cars/', CarListView.as_view(), name='car_list'),
    path('cars/create/', CarCreateView.as_view(), name='car_create'),
    path('cars/<int:pk>/', CarDetailView.as_view(), name='car_detail'),
    path('cars/<int:pk>/edit/', CarUpdateView.as_view(), name='car_update'),

    # Driver URLs
    path('drivers/', DriverListView.as_view(), name='driver_list'),
    path('drivers/create/', DriverCreateView.as_view(), name='driver_create'),
    path('drivers/<int:pk>/', DriverDetailView.as_view(), name='driver_detail'),
    path('drivers/<int:pk>/edit/', DriverUpdateView.as_view(), name='driver_update'),
    path('drivers/assign-user/', DriverUserAssignmentView.as_view(), name='driver_assign_user'),
]