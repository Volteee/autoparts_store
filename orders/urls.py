from django.urls import path
from . import views

urlpatterns = [
    path(
        'delivery-map/<int:pk>/pdf/',
        views.DeliveryMapPDFView.as_view(),
        name='delivery_map_pdf'
    ),
    path(
        'customer-order/<int:pk>/pdf/',
        views.CustomerOrderPDFView.as_view(),
        name='customer_order_pdf'
    ),
    path(
        'supplier-order/<int:pk>/pdf/',
        views.SupplierOrderPDFView.as_view(),
        name='supplier_order_pdf'
    ),
    path(
        'payment-report/',
        views.PaymentReportView.as_view(),
        name='payment_report'
    ),
    path('delivery-orders/', views.DeliveryOrdersListView.as_view(), name='delivery_orders'),
    path('driver-assignment/<int:pk>/update/', views.DriverAssignmentUpdateView.as_view(), name='driver_assignment_update'),
    path('driver-assignment/<int:assignment_id>/generate-docs/', views.generate_delivery_documents, name='generate_delivery_docs'),
    path('driver-assignment/<int:assignment_id>/mark-delivered/', views.mark_as_delivered, name='mark_delivered'),
]