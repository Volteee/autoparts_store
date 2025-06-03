"""
URL configuration for autoparts_store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from users.views import CustomHomeView, CustomLoginView, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('orders/', include('orders.urls')),
    path('dealers/', include('dealers.urls')),
    # Перенаправление корневого URL на главную страницу
    path('', RedirectView.as_view(url='/home/', permanent=True)),

    # Главная страница
    path('home/', CustomHomeView.as_view(), name='home'),
    path('core/', include('core.urls')),

    # Вход/выход
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
]