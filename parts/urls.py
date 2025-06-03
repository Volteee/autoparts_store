from django.urls import path
from . import views

urlpatterns = [
    # PartCategory URLs
    path('categories/', views.PartCategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.PartCategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.PartCategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.PartCategoryDeleteView.as_view(), name='category_delete'),

    # Manufacturer URLs
    path('manufacturers/', views.ManufacturerListView.as_view(), name='manufacturer_list'),
    path('manufacturers/create/', views.ManufacturerCreateView.as_view(), name='manufacturer_create'),
    path('manufacturers/<int:pk>/update/', views.ManufacturerUpdateView.as_view(), name='manufacturer_update'),
    path('manufacturers/<int:pk>/delete/', views.ManufacturerDeleteView.as_view(), name='manufacturer_delete'),

    # Supplier URLs
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/update/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),

    # Part URLs
    path('parts/', views.PartListView.as_view(), name='part_list'),
    path('parts/create/', views.PartCreateView.as_view(), name='part_create'),
    path('parts/<int:pk>/update/', views.PartUpdateView.as_view(), name='part_update'),
    path('parts/<int:pk>/delete/', views.PartDeleteView.as_view(), name='part_delete'),

    # PriceList URLs
    path('pricelists/', views.PriceListListView.as_view(), name='pricelist_list'),
    path('pricelists/create/', views.PriceListCreateView.as_view(), name='pricelist_create'),
    path('pricelists/<int:pk>/delete/', views.PriceListDeleteView.as_view(), name='pricelist_delete'),

    # DeliveryOption URLs
    path('delivery-options/', views.DeliveryOptionListView.as_view(), name='deliveryoption_list'),
    path('delivery-options/create/', views.DeliveryOptionCreateView.as_view(), name='deliveryoption_create'),
    path('delivery-options/<int:pk>/update/', views.DeliveryOptionUpdateView.as_view(), name='deliveryoption_update'),
    path('delivery-options/<int:pk>/delete/', views.DeliveryOptionDeleteView.as_view(), name='deliveryoption_delete'),
]