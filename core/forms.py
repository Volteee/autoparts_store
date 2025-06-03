from django import forms
from .models import Customer, Car, Driver
from django.contrib.auth import get_user_model


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО покупателя'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'}),
        }
        labels = {
            'name': 'ФИО',
            'phone': 'Телефон',
        }


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['customer', 'make', 'model', 'year', 'vin']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'make': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Марка автомобиля'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Модель автомобиля'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2100}),
            'vin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VIN-код (17 символов)'}),
        }
        labels = {
            'customer': 'Владелец',
            'make': 'Марка',
            'model': 'Модель',
            'year': 'Год выпуска',
            'vin': 'VIN',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.all().order_by('name')


class DriverForm(forms.ModelForm):
    def __init__(self, *args, user_role=None, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()

        # Фильтрация пользователей по роли, если указана
        if user_role:
            self.fields['user'].queryset = User.objects.filter(role=user_role)

        for field in self.fields.values():
            if field.widget.__class__.__name__ != 'CheckboxInput':
                field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Driver
        fields = ['user', 'name', 'phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'ФИО водителя'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (XXX) XXX-XX-XX'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'ФИО водителя',
            'phone': 'Телефон',
            'is_active': 'Активен',
        }


class DriverUserAssignmentForm(forms.Form):
    driver = forms.ModelChoiceField(
        queryset=Driver.objects.filter(user__isnull=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Водитель без учетной записи'
    )
    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(role='driver', driver__isnull=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Пользователь (роль "Водитель")'
    )