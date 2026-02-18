from rest_framework import serializers
from .models import Categoria, Moneda, TipoDeuda

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id_categoria', 'nombre', 'descripcion']

        read_only_fields = ['usuario']

class MonedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moneda
        fields = ['id_moneda', 'nombre', 'descripcion']

class TipoDeudaSerializer(serializers.ModelSerializer): 
    class Meta:
        model = TipoDeuda
        fields = ['id_tipo_deuda', 'nombre', 'descripcion']