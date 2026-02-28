from rest_framework import serializers
from .models import Categoria,SubCategoria, Moneda, TipoMovimiento, TipoTransaccion, MetodoPago, CuentaCorriente, MovimientoCuenta, Transaccion

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id_categoria', 'nombre', 'descripcion']

        read_only_fields = ['usuario']

class SubCategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategoria
        fields = ['id_subcategoria', 'nombre', 'descripcion', 'categoria']

        read_only_fields = ['usuario']

class MonedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moneda
        fields = ['id_moneda', 'nombre', 'simbolo']

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
    persona_nombre = serializers.ReadOnlyField(source='persona.nombre')
    moneda_simbolo = serializers.ReadOnlyField(source='moneda.simbolo')

    class Meta:
        model = CuentaCorriente
        fields = '__all__'
        

class MovimientoCuentaSerializer(serializers.ModelSerializer):
    subcategoria_nombre = serializers.ReadOnlyField(source='subcategoria.nombre')
    tipo_movimiento_nombre = serializers.ReadOnlyField(source='tipo_movimiento.nombre')

    class Meta:
        model = MovimientoCuenta
        fields = '__all__'
        read_only_fields = ['fecha_registro','saldo_pendiente']

        

class TransaccionSerializer(serializers.ModelSerializer):
    # Añadimos esta línea mágica para extraer el nombre de la categoría
    subcategoria_nombre = serializers.ReadOnlyField(source='subcategoria.nombre')
    tipo_transaccion_nombre = serializers.ReadOnlyField(source='tipo_transaccion.nombre')
    
    
    class Meta:
        model = Transaccion
        fields = '__all__' # Esto enviará todos los campos + categoria_nombre
        read_only_fields = ['fecha_registro', 'usuario']
        extra_kwargs = {
            'subcategoria': {'required': False},
            'moneda': {'required': False},
            'tipo_transaccion': {'required': False},
        }
        
        
