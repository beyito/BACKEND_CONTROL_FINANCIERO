from django.shortcuts import render
from rest_framework import viewsets, permissions
from django.db.models import Q  # <--- IMPORTANTE
from .models import Categoria, Moneda, TipoMovimiento, TipoTransaccion, MetodoPago, CuentaCorriente, MovimientoCuenta, Transaccion
from .serializers import CategoriaSerializer, MonedaSerializer, TipoMovimientoSerializer, TipoTransaccionSerializer, MetodoPagoSerializer, CuentaCorrienteSerializer, MovimientoCuentaSerializer, TransaccionSerializer
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

class MovimientoCuentaViewSet(viewsets.ModelViewSet):
    queryset = MovimientoCuenta.objects.all()
    serializer_class = MovimientoCuentaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 1. Seguridad: Solo los movimientos de las cuentas de este usuario
        # (Asumiendo que Persona está vinculada al Usuario)
        queryset = MovimientoCuenta.objects.filter(
            cuenta_corriente__persona__usuario=self.request.user
        )
        
        # 2. Leemos el parámetro de la URL (ej: ?cuenta=5)
        cuenta_corriente = self.request.query_params.get('cuenta_corriente')

        # 3. Filtro directo por la llave foránea
        if cuenta_corriente is not None:
            # Como la llave foránea se llama cuenta_corriente, usamos cuenta_corriente_id
            queryset = queryset.filter(cuenta_corriente_id=cuenta_corriente)

        return queryset



class TransaccionViewSet(viewsets.ModelViewSet):
    serializer_class = TransaccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaccion.objects.filter(usuario=self.request.user).order_by('-fecha_registro')

    def perform_create(self, serializer):

        # --- CONSTANTES DE BASE DE DATOS ---
        # Tipos de Movimiento
        MOVIMIENTO_LE_PRESTE_ID = 1
        MOVIMIENTO_ME_PRESTO_ID = 2

        # Tipos de Transacción
        TRANSACCION_INGRESO_ID = 1
        TRANSACCION_EGRESO_ID = 2
        
        movimiento = serializer.validated_data.get('movimiento_cuenta')
        datos_automaticos = {'usuario': self.request.user}

        if movimiento:
            datos_automaticos['categoria'] = movimiento.categoria
            datos_automaticos['persona'] = movimiento.cuenta_corriente.persona
            datos_automaticos['moneda'] = movimiento.cuenta_corriente.moneda

            # --- LA MAGIA OPTIMIZADA ---
            # Usamos .tipo_movimiento_id para NO hacer una consulta extra a la BD
            id_movimiento = movimiento.tipo_movimiento_id

            if id_movimiento == MOVIMIENTO_LE_PRESTE_ID:
                # Yo presté -> El pago que recibo es un INGRESO
                # Usamos _id para asignar directamente el entero sin buscar el objeto
                datos_automaticos['tipo_transaccion_id'] = TRANSACCION_INGRESO_ID
                
            elif id_movimiento == MOVIMIENTO_ME_PRESTO_ID:
                # Me prestaron -> El pago que hago es un EGRESO
                datos_automaticos['tipo_transaccion_id'] = TRANSACCION_EGRESO_ID

        # Guardamos la transacción con los datos perfectos
        transaccion = serializer.save(**datos_automaticos)

        # La matemática de saldos (aplica igual para ambos casos)
        if transaccion.movimiento_cuenta:
            prestamo = transaccion.movimiento_cuenta
            prestamo.saldo_pendiente -= transaccion.monto
            prestamo.save()

    def perform_destroy(self, instance):
        if instance.movimiento_cuenta:
            prestamo = instance.movimiento_cuenta
            prestamo.saldo_pendiente += instance.monto
            prestamo.save()
        super().perform_destroy(instance)
