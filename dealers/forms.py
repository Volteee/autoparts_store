from django import forms

class DealerDistributionForm(forms.Form):
    include_inactive = forms.BooleanField(
        label='Включая неактивных дилеров',
        required=False,
        help_text='Отметьте, чтобы включить дилеров, помеченных как неактивные'
    )