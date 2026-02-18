"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
# config/urls.py (o donde tengas tus rutas principales)
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # <--- Esta es tu vista de LOGIN
    TokenRefreshView,     # <--- Esta es para refrescar el token
)
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('finance/', include('finance.urls')),
    path('api/', include('usuario.urls')),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('finance/', include('finance.urls')),
]
