from django.urls import path, include
from ia import views
urlpatterns = [
path('transaccion/', views.procesar_compras_por_voz, name='procesar_dictado'),
]