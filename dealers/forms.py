from django import forms

class DealerDistributionForm(forms.Form):
    include_inactive = forms.BooleanField(
        label='Включая неактивных дилеров',
        required=False,
        help_text='Отметьте, чтобы включить дилеров, помеченных как неактивные'
    )


from django import forms
from .models import Dealer, DealerStockNorm, DealerDistributionReport, DealerWaybill
from core.models import Customer


class DealerForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        label='Клиент',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Dealer
        fields = ['customer', 'email', 'contact_person', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DealerStockNormForm(forms.ModelForm):
    class Meta:
        model = DealerStockNorm
        fields = ['dealer', 'part', 'norm']
        widgets = {
            'dealer': forms.Select(attrs={'class': 'form-select'}),
            'part': forms.Select(attrs={'class': 'form-select'}),
            'norm': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class FileUploadForm(forms.Form):
    dealer_file = forms.FileField(
        label='Файл дилера',
        help_text='Загрузите Excel-файл с данными дилера'
    )

class DealerWaybillGenerationForm(forms.Form):
    report = forms.ModelChoiceField(
        queryset=DealerDistributionReport.objects.all(),
        label='Отчет',
        widget=forms.Select(attrs={'class': 'form-select'}))
    dealer = forms.ModelChoiceField(
        queryset=Dealer.objects.all(),
        label='Дилер',
        widget=forms.Select(attrs={'class': 'form-select'}))