from django.shortcuts import render
from rest_framework import viewsets,generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UsuarioSerializer, PersonaSerializer
from .models import Usuario, Persona
# Create your views here.
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer

    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Aquí inyectas el usuario que viene en el request (Token)
        serializer.save(usuario=self.request.user)

    # Opcional: Para que cada quien vea SOLO sus personas
    def get_queryset(self):
        return Persona.objects.filter(usuario=self.request.user, activo=True)
    
    def perform_destroy(self, instance):
        # Solo lo ocultamos
        instance.activo = False
        instance.save()
class MiPerfilView(generics.RetrieveUpdateAPIView):
    # ¡Usamos tu serializador!
    serializer_class = UsuarioSerializer 
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Esta es la clave: en lugar de buscar por ID en la URL, 
        # devuelve automáticamente al dueño del token que hace la petición.
        return self.request.user