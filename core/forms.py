from django import forms
from .models import Log, List, Film
from datetime import date

from django.contrib.admin.widgets import FilteredSelectMultiple

class LogForm(forms.ModelForm):
    date = forms.DateField(initial=date.today(), label='Watched on', widget=forms.TextInput(attrs={'class': 'log-date', 'type':'date'}))
    rating = forms.DecimalField(decimal_places=1, max_digits=2, min_value=0, max_value=5, help_text=' / 5.0', widget=forms.NumberInput(attrs={'class': 'log-rating', 'placeholder': '0.0'}))

    class Meta:
        model = Log
        fields = ['date', 'rating']

class NewListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ['title', 'ordered', 'description']
        labels = {
            'ordered': 'Ordered list'
        }