from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False

        if self.request.user.is_superuser:
            return True

        if self.request.user.role in self.allowed_roles:
            return True

        raise PermissionDenied("У вас нет прав для доступа к этой странице")