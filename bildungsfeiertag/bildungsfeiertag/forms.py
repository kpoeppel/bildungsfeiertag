from django import forms
from .models import User, Event
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django_registration.forms import RegistrationForm


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = User
        fields = ('username', 'email')


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
        field_classes = {'username': UsernameField}

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get('password')


class UserRegistrationForm(RegistrationForm):

    class Meta(RegistrationForm.Meta):
        model = User
        fields = ['email', 'username']


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ['title', 'description', 'duration', 'max_participants',
                  'type', 'active']
