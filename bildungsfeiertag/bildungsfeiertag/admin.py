from django.contrib import admin
from . import models
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, ProfileForm
from .models import User

admin.site.register(models.Site)
admin.site.register(models.Room)
admin.site.register(models.Event)
admin.site.register(models.Vote)
admin.site.register(models.Registration)
admin.site.register(models.Interest)
admin.site.register(models.ScheduledEvent)
admin.site.register(models.Helper)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = ProfileForm
    model = User
    list_display = ['email', 'username', ]


admin.site.register(User, CustomUserAdmin)
