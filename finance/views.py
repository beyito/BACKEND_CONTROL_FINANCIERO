from django.shortcuts import render
from rest_framework import viewsets, permissions
from django.db.models import Q  # <--- IMPORTANTE
from .models import Categoria, Moneda, TipoMovimiento, TipoTransaccion, MetodoPago, CuentaCorriente, MovimientoCuenta
from .serializers import CategoriaSerializer, MonedaSerializer, TipoMovimientoSerializer, TipoTransaccionSerializer, MetodoPagoSerializer, CuentaCorrienteSerializer, MovimientoCuentaSerializer
from .permissions import IsOwnerOrGlobalReadOnly, IsAdminOrReadOnly 

class CategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrGlobalReadOnly]

    # 1. FILTRADO INTELIGENTE
    def get_queryset(self):
        user = self.request.user
        # Lógica: (Usuario es el actual) O (Usuario es Nulo)
        return Categoria.objects.filter(
            Q(usuario=user) | Q(usuario__isnull=True)
        )

    # 2. CREACIÓN AUTOMÁTICA
    def perform_create(self, serializer):
        # Cuando un usuario crea una categoría, SIEMPRE se le asigna su usuario.
        # Así evitas que usuarios normales creen categorías globales por error.
        serializer.save(usuario=self.request.user)

class MonedaViewSet(viewsets.ModelViewSet):
    queryset = Moneda.objects.all()
    serializer_class = MonedaSerializer
    # AQUÍ ESTÁ LA MAGIA:
    permission_classes = [IsAdminOrReadOnly]

class TipoMovimientoViewSet(viewsets.ModelViewSet):
    queryset = TipoMovimiento.objects.all()
    serializer_class = TipoMovimientoSerializer
    permission_classes = [IsAdminOrReadOnly]

class TipoTransaccionViewSet(viewsets.ModelViewSet):
    queryset = TipoTransaccion.objects.all()
    serializer_class = TipoTransaccionSerializer
    permission_classes = [IsAdminOrReadOnly]

class MetodoPagoViewSet(viewsets.ModelViewSet):
    queryset = MetodoPago.objects.all()
    serializer_class = MetodoPagoSerializer
    permission_classes = [IsAdminOrReadOnly]

class CuentaCorrienteViewSet(viewsets.ModelViewSet):
    queryset = CuentaCorriente.objects.all()
    serializer_class = CuentaCorrienteSerializer
    permission_classes = [permissions.IsAuthenticated]

# class MovimientoCuentaViewSet(viewsets.ModelViewSet):
#     queryset = MovimientoCuenta.objects.all()
#     serializer_class = MovimientoCuentaSerializer
#     permission_classes = [permissions.IsAuthenticated]