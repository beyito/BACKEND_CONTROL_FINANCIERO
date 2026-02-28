from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Categoria, Moneda, TipoMovimiento, TipoTransaccion, MetodoPago, CuentaCorriente, MovimientoCuenta, Transaccion, SubCategoria
from .serializers import CategoriaSerializer, MonedaSerializer, TipoMovimientoSerializer, TipoTransaccionSerializer, MetodoPagoSerializer, CuentaCorrienteSerializer, MovimientoCuentaSerializer, TransaccionSerializer, SubCategoriaSerializer
from .permissions import IsOwnerOrGlobalReadOnly, IsAdminOrReadOnly 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q

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

class SubCategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = SubCategoriaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrGlobalReadOnly]

    # 1. FILTRADO INTELIGENTE
    def get_queryset(self):
        user = self.request.user
        # Lógica: (Usuario es el actual) O (Usuario es Nulo)
        return SubCategoria.objects.filter(
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
    def perform_create(self, serializer):
        # 1. Guardamos el Movimiento de Cuenta (el "contrato")
        movimiento = serializer.save()

        # 2. Extraemos los datos necesarios para la Transacción Automática
        cuenta = movimiento.cuenta_corriente
        usuario = self.request.user
        persona = cuenta.persona
        moneda = cuenta.moneda
        monto = movimiento.monto_inicial

        # --- CONSTANTES ---
        # Revisa que estos IDs coincidan con los de tu tabla tipo_movimiento
        TIPO_MOVIMIENTO_LE_PRESTE_ID = 1
        TIPO_MOVIMIENTO_ME_PRESTO_ID = 2

        # Revisa que estos IDs coincidan con los de tu tabla tipo_transaccion
        TIPO_TRANSACCION_INGRESO_ID = 1
        TIPO_TRANSACCION_EGRESO_ID = 2

        # Asumimos que el desembolso del préstamo se da en Efectivo (id=1) 
        # Ya que en la pantalla móvil no pedimos el método de pago para el contrato.
        metodo_pago_id = self.request.data.get('metodo_pago_id', 1)

        tipo_mov_id = movimiento.tipo_movimiento_id
        
        # 3. Lógica para determinar Ingreso/Egreso y la Subcategoría
        tipo_transaccion_id = None
        subcategoria_nombre = None

        if tipo_mov_id == TIPO_MOVIMIENTO_LE_PRESTE_ID:
            # Yo presté -> Salió dinero de mi bolsillo físico (Egreso)
            tipo_transaccion_id = TIPO_TRANSACCION_EGRESO_ID
            subcategoria_nombre = 'Dinero que presté'

        elif tipo_mov_id == TIPO_MOVIMIENTO_ME_PRESTO_ID:
            # Me prestaron -> Entró dinero a mi bolsillo físico (Ingreso)
            tipo_transaccion_id = TIPO_TRANSACCION_INGRESO_ID
            subcategoria_nombre = 'Dinero que me prestaron'

        # 4. Buscamos la subcategoría en la base de datos y creamos la transacción
        if tipo_transaccion_id and subcategoria_nombre:
            subcat = SubCategoria.objects.filter(nombre=subcategoria_nombre).first()
            
            if subcat:
                Transaccion.objects.create(
                    usuario=usuario,
                    movimiento_cuenta=movimiento, # Vinculamos la transacción a este préstamo
                    persona=persona,
                    subcategoria=subcat,
                    tipo_transaccion_id=tipo_transaccion_id,
                    metodo_pago_id=metodo_pago_id,
                    moneda=moneda,
                    monto=monto
                )
                
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
        queryset = Transaccion.objects.filter(usuario=self.request.user).order_by('-fecha_registro')
        movimiento_cuenta = self.request.query_params.get('movimiento_cuenta')
        if movimiento_cuenta is not None:
            # Como la llave foránea se llama cuenta_corriente, usamos cuenta_corriente_id
            queryset = queryset.filter(movimiento_cuenta_id=movimiento_cuenta)

        return queryset

    def perform_create(self, serializer):

        # --- CONSTANTES DE BASE DE DATOS ---
        # Tipos de Movimiento
        MOVIMIENTO_LE_PRESTE_ID = 1
        MOVIMIENTO_ME_PRESTO_ID = 2

        # Tipos de Transacción
        TRANSACCION_INGRESO_ID = 1
        TRANSACCION_EGRESO_ID = 2
        
        # Subcategorías para los pagos de las deudas (¡Nuevas constantes!)
        SUBCATEGORIA_COBRO_DEUDA_ID = 44
        SUBCATEGORIA_PAGO_DEUDA_ID = 45
        
        movimiento = serializer.validated_data.get('movimiento_cuenta')
        datos_automaticos = {'usuario': self.request.user}

        if movimiento:
            # Heredamos persona y moneda del contrato
            datos_automaticos['persona'] = movimiento.cuenta_corriente.persona
            datos_automaticos['moneda'] = movimiento.cuenta_corriente.moneda

            # --- LA MAGIA OPTIMIZADA ---
            # Usamos _id para NO hacer una consulta extra a la BD
            id_movimiento = movimiento.tipo_movimiento_id

            if id_movimiento == MOVIMIENTO_LE_PRESTE_ID:
                # Yo presté -> El pago que recibo es un INGRESO
                datos_automaticos['tipo_transaccion_id'] = TRANSACCION_INGRESO_ID
                # Asignamos la subcategoría "Cobro de deuda" (ID 44)
                datos_automaticos['subcategoria_id'] = SUBCATEGORIA_COBRO_DEUDA_ID
                
            elif id_movimiento == MOVIMIENTO_ME_PRESTO_ID:
                # Me prestaron -> El pago que hago es un EGRESO
                datos_automaticos['tipo_transaccion_id'] = TRANSACCION_EGRESO_ID
                # Asignamos la subcategoría "Pago de deuda" (ID 45)
                datos_automaticos['subcategoria_id'] = SUBCATEGORIA_PAGO_DEUDA_ID

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





class ResumenDashboardView(APIView):
    permission_classes = [IsAuthenticated] # Protegemos la ruta con JWT

    def get(self, request):
        # Filtramos solo las transacciones del usuario que inició sesión
        transacciones_usuario = Transaccion.objects.filter(usuario=request.user)

        # 1. Sumamos todas las entradas directamente en la base de datos
        entradas = transacciones_usuario.filter(
            Q(tipo_transaccion__nombre__icontains='entrada') | 
            Q(tipo_transaccion__nombre__icontains='ingreso')
        ).aggregate(total=Sum('monto'))['total'] or 0

        # 2. Sumamos todas las salidas
        salidas = transacciones_usuario.filter(
            Q(tipo_transaccion__nombre__icontains='salida') | 
            Q(tipo_transaccion__nombre__icontains='gasto') |
            Q(tipo_transaccion__nombre__icontains='egreso')
        ).aggregate(total=Sum('monto'))['total'] or 0

        # 3. Calculamos el saldo global
        saldo_global = entradas - salidas

        return Response({
            'saldo_global': float(saldo_global),
            'total_entradas': float(entradas),
            'total_salidas': float(salidas)
        })