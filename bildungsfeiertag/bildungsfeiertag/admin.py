from django.contrib import admin
from . import models

admin.site.register(models.Site)
admin.site.register(models.Room)
admin.site.register(models.Event)
admin.site.register(models.Vote)
admin.site.register(models.Registration)
admin.site.register(models.Interest)
