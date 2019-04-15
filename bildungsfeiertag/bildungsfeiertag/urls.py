"""bildungsfeiertag URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from . import views


urlpatterns = [
    path(r"admin/", admin.site.urls),
    path(r"", views.index),
    path(r"about", views.about),
    path(r"site/<str:site_name>", views.site),
    path(r"site/<str:site_name>/event/<str:event_title>", views.event),
    path(r"site/<str:site_name>/room/<str:room_name>", views.room),
]
