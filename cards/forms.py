from django import forms
from .models import Card

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = [
            'card_number',
            'card_holder',
            'card_type',
            'card_system',
            'bank_name',
            'balance',
            'expiry_date',
            'is_active',
            'color',
            'description',
        ]
        widgets = {
            'card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0000 0000 0000 0000'
            }),
            'card_holder': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IVAN IVANOV'}),
            'card_type': forms.Select(attrs={'class': 'form-select'}),
            'card_system': forms.Select(attrs={'class': 'form-select'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VTB'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_card_number(self):
        number = self.cleaned_data.get('card_number', '')
        normalized = ''.join(ch for ch in number if ch.isdigit())
        if not 12 <= len(normalized) <= 19:
            raise forms.ValidationError('Введите корректный номер карты (12-19 цифр).')

        return normalized
