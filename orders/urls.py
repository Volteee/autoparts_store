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

    path('customer-orders/', views.CustomerOrderListView.as_view(), name='customer_order_list'),
    path('customer-orders/create/', views.CustomerOrderCreateView.as_view(), name='customer_order_create'),
    path('customer-orders/<int:pk>/', views.CustomerOrderDetailView.as_view(), name='customer_order_detail'),
    path('customer-orders/<int:pk>/update/', views.CustomerOrderUpdateView.as_view(), name='customer_order_update'),

    # OrderItem URLs
    path('customer-orders/<int:order_pk>/items/create/', views.OrderItemCreateView.as_view(), name='order_item_create'),
    path('order-items/<int:pk>/update/', views.OrderItemUpdateView.as_view(), name='order_item_update'),

    # DeliveryMap URLs
    path('delivery-maps/<int:pk>/', views.DeliveryMapDetailView.as_view(), name='delivery_map_detail'),

    # DeliveryMapItem URLs
    path('delivery-map-items/<int:pk>/update/', views.DeliveryMapItemUpdateView.as_view(),
         name='delivery_map_item_update'),

    # SupplierOrder URLs
    path('supplier-orders/', views.SupplierOrderListView.as_view(), name='supplier_order_list'),
    path('supplier-orders/create/', views.SupplierOrderCreateView.as_view(), name='supplier_order_create'),
    path('supplier-orders/<int:pk>/update/', views.SupplierOrderUpdateView.as_view(), name='supplier_order_update'),

    # GoodsReceipt URLs
    path('goods-receipts/', views.GoodsReceiptListView.as_view(), name='goods_receipt_list'),
    path('goods-receipts/create/', views.GoodsReceiptCreateView.as_view(), name='goods_receipt_create'),

    # SupplierPayment URLs
    path('supplier-payments/', views.SupplierPaymentListView.as_view(), name='supplier_payment_list'),
    path('supplier-payments/create/', views.SupplierPaymentCreateView.as_view(), name='supplier_payment_create'),

    # DriverAssignment URLs
    path('driver-assignments/', views.DriverAssignmentListView.as_view(), name='driver_assignment_list'),
    path('driver-assignments/create/', views.DriverAssignmentCreateView.as_view(), name='driver_assignment_create'),
    path('driver-assignments/<int:pk>/update/', views.MyDriverAssignmentUpdateView.as_view(),
         name='driver_assignment_update'),
]