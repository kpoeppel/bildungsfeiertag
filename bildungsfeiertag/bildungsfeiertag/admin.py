from django.contrib import admin
from django.db import models
from .models import *

admin.site.register(Site)
admin.site.register(Room)
admin.site.register(Talk)
admin.site.register(Vote)
