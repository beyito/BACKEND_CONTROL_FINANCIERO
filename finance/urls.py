# usuario/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MonedaViewSet, CategoriaViewSet, TipoMovimientoViewSet, TipoTransaccionViewSet, MetodoPagoViewSet, CuentaCorrienteViewSet


# 1. Creamos el Router
router = DefaultRouter()

# 2. Registramos tu ViewSet
# 'moneda' -> será el prefijo de la URL (ej: /moneda/)
router.register(r'moneda', MonedaViewSet, basename='moneda')
router.register(r'categoria', CategoriaViewSet, basename='categoria')  
router.register(r'tipomovimiento', TipoMovimientoViewSet, basename='tipomovimiento')  
router.register(r'tipotransaccion', TipoTransaccionViewSet, basename='tipotransaccion')
router.register(r'metodopago', MetodoPagoViewSet, basename='metodopago')
router.register(r'cuentacorriente', CuentaCorrienteViewSet, basename='cuentacorriente')

# 3. Definimos las URLs
urlpatterns = [
    path('', include(router.urls)),

]