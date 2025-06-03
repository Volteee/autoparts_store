from django.urls import path
from . import views

urlpatterns = [
    # Дилеры
    path('dealers/', views.DealerListView.as_view(), name='dealer_list'),
    path('dealers/create/', views.DealerCreateView.as_view(), name='dealer_create'),
    path('dealers/<int:pk>/update/', views.DealerUpdateView.as_view(), name='dealer_update'),
    path('dealers/<int:pk>/delete/', views.DealerDeleteView.as_view(), name='dealer_delete'),

    # Нормы запасов
    path('stock-norms/', views.DealerStockNormListView.as_view(), name='stock_norm_list'),
    path('stock-norms/create/', views.DealerStockNormCreateView.as_view(), name='stock_norm_create'),
    path('stock-norms/<int:pk>/update/', views.DealerStockNormUpdateView.as_view(), name='stock_norm_update'),

    # Файлы
    path('generate-files/', views.GenerateDealerFilesView.as_view(), name='generate_files'),
    path('process-files/', views.ProcessDealerFilesView.as_view(), name='process_files'),
    path('upload-file/', views.FileUploadView.as_view(), name='upload_file'),

    # Отчеты
    path('reports/', views.DealerDistributionReportListView.as_view(), name='report_list'),
    path('reports/<int:pk>/generate/', views.GenerateReportView.as_view(), name='generate_report'),

    # Накладные
    path('waybills/', views.DealerWaybillListView.as_view(), name='waybill_list'),
    path('generate-waybill/', views.GenerateWaybillView.as_view(), name='generate_waybill'),

    # Распределение (из существующего)
    path('distribution/', views.DealerDistributionView.as_view(), name='dealer_distribution'),
]