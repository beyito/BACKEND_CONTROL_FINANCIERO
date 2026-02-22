from rest_framework import serializers
from .models import Categoria, Moneda, TipoMovimiento, TipoTransaccion, MetodoPago, CuentaCorriente, MovimientoCuenta, Transaccion

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id_categoria', 'nombre', 'descripcion']

        read_only_fields = ['usuario']

class MonedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moneda
        fields = ['id_moneda', 'nombre', 'descripcion']

class TipoMovimientoSerializer(serializers.ModelSerializer): 
    class Meta:
        model = TipoMovimiento
        fields = ['id_tipo_movimiento', 'nombre', 'descripcion']

class TipoTransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTransaccion
        fields = ['id_tipo_transaccion', 'nombre', 'descripcion']

class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = ['id_metodo_pago', 'nombre', 'descripcion']

class CuentaCorrienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaCorriente
        fields = ['id_cuenta_corriente', 'persona', 'moneda']

# class MovimientoCuentaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MovimientoCuenta
#         fields = ['id_movimiento_cuenta', 'cuenta_corriente', 'categoria', 'tipo_movimiento', 'fecha_registro', 'monto_inicial', 'saldo_pendiente']

#         read_only_fields = ['saldo_pendiente']

