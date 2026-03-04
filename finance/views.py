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

    def get_queryset(self):
        # Solo las cuentas corrientes vinculadas a personas del usuario actual
        return CuentaCorriente.objects.filter(persona__usuario=self.request.user)

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
        concepto = movimiento.concepto

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
                    monto=monto,
                    concepto=concepto,
                )
                
    def get_queryset(self):
        # 1. Seguridad: Solo los movimientos de las cuentas de este usuario
        # (Asumiendo que Persona está vinculada al Usuario)
        queryset = MovimientoCuenta.objects.filter(
            cuenta_corriente__persona__usuario=self.request.user, activo=True
        )
        
        # 2. Leemos el parámetro de la URL (ej: ?cuenta=5)
        cuenta_corriente = self.request.query_params.get('cuenta_corriente')

        # 3. Filtro directo por la llave foránea
        if cuenta_corriente is not None:
            # Como la llave foránea se llama cuenta_corriente, usamos cuenta_corriente_id
            queryset = queryset.filter(cuenta_corriente_id=cuenta_corriente)

        return queryset

    def perform_destroy(self, instance):
        # 1. Ocultamos el contrato principal (El préstamo)
        instance.activo = False
        instance.save()

        # 2. Buscamos todas las transacciones asociadas a este préstamo
        # (Django crea automáticamente el sufijo _set para las relaciones inversas)
        transacciones_asociadas = instance.transaccion_set.all()

        # 3. Ocultamos todas sus transacciones (desembolso inicial y cuotas pagadas)
        for tx in transacciones_asociadas:
            tx.activo = False
            tx.save()

class TransaccionViewSet(viewsets.ModelViewSet):
    serializer_class = TransaccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        
        queryset = Transaccion.objects.filter(usuario=self.request.user, activo=True).order_by('-fecha_registro')
        movimiento_cuenta = self.request.query_params.get('movimiento_cuenta')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            # Filtramos el rango. Usamos "__range" en Django.
            queryset = queryset.filter(fecha_registro__date__range=[fecha_inicio, fecha_fin])

        if movimiento_cuenta is not None:
            # Como la llave foránea se llama cuenta_corriente, usamos cuenta_corriente_id
            queryset = queryset.filter(movimiento_cuenta_id=movimiento_cuenta)

        return queryset.order_by('-fecha_registro')

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
        # 1. Cambiamos el estado en lugar de borrarlo
        instance.activo = False
        instance.save()

        # 2. Revertimos la matemática del préstamo (si aplica)
        if instance.movimiento_cuenta:
            prestamo = instance.movimiento_cuenta
            prestamo.saldo_pendiente += instance.monto # Le devolvemos la deuda
            prestamo.save()
            
    def perform_update(self, serializer):
        # Constantes de subcategorías (Ajusta los IDs si en tu BD son diferentes)
        # Asumimos que 44 y 45 son pagos/cuotas. Cualquier otra es la transacción Padre.
        SUBCATEGORIA_COBRO_DEUDA_ID = 44
        SUBCATEGORIA_PAGO_DEUDA_ID = 45

        # 1. Recuperar los datos ANTES de que se modifiquen
        transaccion_antigua = self.get_object()
        monto_antiguo = transaccion_antigua.monto
        movimiento_antiguo = transaccion_antigua.movimiento_cuenta
        subcat_antigua_id = transaccion_antigua.subcategoria_id

        # 2. Guardar los nuevos datos
        transaccion_nueva = serializer.save()

        # 3. La Matemática Avanzada
        if movimiento_antiguo == transaccion_nueva.movimiento_cuenta:
            # CASO A: Mismo préstamo
            if transaccion_nueva.movimiento_cuenta:
                prestamo = transaccion_nueva.movimiento_cuenta
                es_cuota = transaccion_nueva.subcategoria_id in [SUBCATEGORIA_COBRO_DEUDA_ID, SUBCATEGORIA_PAGO_DEUDA_ID]
                
                if es_cuota:
                    # Es un PAGO: Anulamos el pago viejo y restamos el pago nuevo
                    prestamo.saldo_pendiente = prestamo.saldo_pendiente + monto_antiguo - transaccion_nueva.monto
                else:
                    # Es el CAPITAL INICIAL (Transacción Padre)
                    diferencia = transaccion_nueva.monto - monto_antiguo
                    prestamo.monto_inicial += diferencia
                    # Si el préstamo total sube, la deuda pendiente sube exactamente igual
                    prestamo.saldo_pendiente += diferencia 
                    
                prestamo.save()

        else:
            # CASO B: Cambió de préstamo vinculado (Muy raro, pero a prueba de balas)
            
            # A. Revertimos los números en el préstamo viejo
            if movimiento_antiguo:
                es_cuota_antigua = subcat_antigua_id in [SUBCATEGORIA_COBRO_DEUDA_ID, SUBCATEGORIA_PAGO_DEUDA_ID]
                if es_cuota_antigua:
                    movimiento_antiguo.saldo_pendiente += monto_antiguo # Le devolvemos la cuota
                else:
                    movimiento_antiguo.monto_inicial -= monto_antiguo # Le quitamos el capital
                    movimiento_antiguo.saldo_pendiente -= monto_antiguo
                movimiento_antiguo.save()
            
            # B. Aplicamos los números al préstamo nuevo
            if transaccion_nueva.movimiento_cuenta:
                prestamo_nuevo = transaccion_nueva.movimiento_cuenta
                es_cuota_nueva = transaccion_nueva.subcategoria_id in [SUBCATEGORIA_COBRO_DEUDA_ID, SUBCATEGORIA_PAGO_DEUDA_ID]
                
                if es_cuota_nueva:
                    prestamo_nuevo.saldo_pendiente -= transaccion_nueva.monto
                else:
                    prestamo_nuevo.monto_inicial += transaccion_nueva.monto
                    prestamo_nuevo.saldo_pendiente += transaccion_nueva.monto
                prestamo_nuevo.save()



class ResumenDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. Filtramos las transacciones válidas del usuario
        transacciones_usuario = Transaccion.objects.filter(usuario=request.user, activo=True)

        # 2. LA MAGIA DE DJANGO: Agrupamos por moneda y sumamos condicionalmente en 1 sola consulta
        resumen = transacciones_usuario.values('moneda').annotate(
            entradas=Sum('monto', filter=
                Q(tipo_transaccion__nombre__icontains='entrada') | 
                Q(tipo_transaccion__nombre__icontains='ingreso')
            ),
            salidas=Sum('monto', filter=
                Q(tipo_transaccion__nombre__icontains='salida') | 
                Q(tipo_transaccion__nombre__icontains='gasto') |
                Q(tipo_transaccion__nombre__icontains='egreso')
            )
        )

        # 3. Formateamos la respuesta en un diccionario limpio
        resultado = {}
        for item in resumen:
            if item['moneda']: # Validamos que la transacción tenga una moneda asignada
                moneda_id = str(item['moneda'])
                entradas = item['entradas'] or 0
                salidas = item['salidas'] or 0
                
                resultado[moneda_id] = {
                    'saldo_global': float(entradas - salidas),
                    'total_entradas': float(entradas),
                    'total_salidas': float(salidas)
                }

        return Response(resultado)