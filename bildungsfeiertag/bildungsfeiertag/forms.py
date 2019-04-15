from django import forms
from .models import Event, Site
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator

class ProfileForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    email = forms.EmailField(label='Email', max_length=100)


class EventForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    email = forms.EmailField(label='Email', max_length=100)
    description = forms.CharField(max_length=1000)
    type = forms.ChoiceField(choices=Event.EVENT_TYPES)
    duration = forms.ChoiceField(choices=((25, "kurz (20 min)"),
                                          (55, "lang (50 min)"),
                                          (85, "sehr lang (80 min)")))
    max_participants = forms.IntegerField(min_value=5, max_value=1000)
    expenses = MoneyField(max_digits=4,
                          decimal_places=2,
                          default_currency='EUR',
                          default=0,
                          validators=[
                            MinMoneyValidator(0),
                            MaxMoneyValidator(20)])
