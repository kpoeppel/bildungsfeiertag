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
from django.conf.urls import url
from . import views


urlpatterns = [
    path(r"admin/", admin.site.urls),
    path(r"", views.index_view),
    path(r"about", views.about_view),
    path(r"site/<str:site_name>", views.site_view),
    path(r"site/<str:site_name>/event_change/<str:event_title>", views.event_change_view),
    path(r"site/<str:site_name>/event_create", views.event_create_view),
    path(r"site/<str:site_name>/event/<str:event_title>", views.event_view),
    path(r"site/<str:site_name>/event/<str:event_title>/delete", views.event_delete_view),
    path(r"site/<str:site_name>/room/<str:room_name>", views.room_view),
    path(r"site/<str:site_name>/helper-information", views.helper_check_view),
    path(r"accounts/register/", views.register_view),
    url(r'^accounts/', include('django_registration.backends.activation.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    path(r"accounts/profile/", views.profile_view),
]
