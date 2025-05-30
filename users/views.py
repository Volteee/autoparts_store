from django.contrib.auth.views import LoginView
from .forms import CustomAuthenticationForm

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = CustomAuthenticationForm


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('/')


from django.views.generic import TemplateView


class CustomHomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['welcome_message'] = (
                f"Добро пожаловать, {self.request.user.get_full_name() or self.request.user.username}!"
            )

            if self.request.user.role == 'operator':
                context['quick_actions'] = [
                    {'url': '/orders/create/', 'label': 'Создать новый заказ', 'icon': 'bi-plus-circle'},
                    {'url': '/orders/', 'label': 'Просмотреть мои заказы', 'icon': 'bi-list-check'},
                ]

            elif self.request.user.role == 'parts_manager':
                context['quick_actions'] = [
                    {'url': '/orders/process/', 'label': 'Обработать заказы', 'icon': 'bi-gear'},
                    {'url': '/parts/', 'label': 'Каталог деталей', 'icon': 'bi-search'},
                ]

            elif self.request.user.role == 'supply_manager':
                context['quick_actions'] = [
                    {'url': '/suppliers/orders/', 'label': 'Заказы поставщикам', 'icon': 'bi-truck'},
                    {'url': '/suppliers/reports/', 'label': 'Отчеты по платежам', 'icon': 'bi-cash-coin'},
                ]

            elif self.request.user.role == 'storekeeper':
                context['quick_actions'] = [
                    {'url': '/warehouse/receipts/', 'label': 'Приходные накладные', 'icon': 'bi-clipboard-check'},
                    {'url': '/warehouse/inventory/', 'label': 'Инвентаризация', 'icon': 'bi-clipboard-data'},
                ]

            elif self.request.user.role == 'delivery_manager':
                context['quick_actions'] = [
                    {'url': '/delivery/schedule/', 'label': 'График доставок', 'icon': 'bi-calendar-event'},
                    {'url': '/delivery/reports/', 'label': 'Отчеты по доставкам', 'icon': 'bi-graph-up'},
                ]

        return context