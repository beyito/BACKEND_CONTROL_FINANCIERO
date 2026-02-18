from rest_framework import serializers
from .models import Usuario,Persona

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username','password', 'email','first_name','last_name', 'fecha_nacimiento']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # 1. PARA CREAR USUARIO (POST)
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data) # Crea la instancia sin guardar aún
        
        if password is not None:
            instance.set_password(password) # Aquí ocurre la magia del Hash
            
        instance.save()
        return instance

    # 2. PARA ACTUALIZAR USUARIO (PUT/PATCH)
    # Esto es vital: si el usuario cambia su contraseña en "Editar Perfil", 
    # también hay que hashearla de nuevo.
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password is not None:
            instance.set_password(password) # Hasheamos la nueva contraseña
            
        instance.save()
        return instance
    
class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ['id_persona', 'usuario', 'nombre', 'fecha_registro', 'descripcion']

        # ESTO ES LA CLAVE:
        read_only_fields = ['usuario']
