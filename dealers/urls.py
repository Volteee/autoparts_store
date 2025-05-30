from django.urls import path
from . import views

urlpatterns = [
    path('distribution/', views.DealerDistributionView.as_view(), name='dealer_distribution'),
]