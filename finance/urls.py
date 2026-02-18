# usuario/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MonedaViewSet, CategoriaViewSet, TipoDeudaViewSet


# 1. Creamos el Router
router = DefaultRouter()

# 2. Registramos tu ViewSet
# 'moneda' -> será el prefijo de la URL (ej: /moneda/)
router.register(r'moneda', MonedaViewSet, basename='moneda')
router.register(r'categoria', CategoriaViewSet, basename='categoria')  
router.register(r'tipodeuda', TipoDeudaViewSet, basename='tipodeuda')  

# 3. Definimos las URLs
urlpatterns = [
    path('', include(router.urls)),

]