# usuario/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, PersonaViewSet, MiPerfilView


# 1. Creamos el Router
router = DefaultRouter()

# 2. Registramos tu ViewSet
# 'usuario' -> será el prefijo de la URL (ej: /usuario/)
router.register(r'usuario', UsuarioViewSet, basename='usuario')
router.register(r'persona', PersonaViewSet, basename='persona')  # Si tienes un ViewSet para Persona, regístralo aquí también
# 3. Definimos las URLs
urlpatterns = [
    path('', include(router.urls)), # Si tienes un ViewSet para Persona, regístralo aquí también
    path('perfil/', MiPerfilView.as_view(), name='perfil'),
]