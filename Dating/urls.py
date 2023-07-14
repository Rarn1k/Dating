"""
URL configuration for Dating project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from auth.viewsets.login import LoginViewSet
from auth.viewsets.refresh import RefreshViewSet
from auth.viewsets.reigster import RegisterViewSet
from user.views import UserViewSet

router = SimpleRouter()

# User
router.register(r'list', UserViewSet, basename='clients')

# Auth
router.register(r'clients/create', RegisterViewSet, basename='clients-register')
router.register(r'clients/login', LoginViewSet, basename='clients-login')
router.register(r'clients/refresh', RefreshViewSet, basename='clients-refresh')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
