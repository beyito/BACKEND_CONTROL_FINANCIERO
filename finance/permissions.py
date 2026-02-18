# finance/permissions.py
from rest_framework import permissions

class IsOwnerOrGlobalReadOnly(permissions.BasePermission):
    """
    - Cualquiera puede VER (GET) las categorías globales.
    - Nadie (salvo admin) puede EDITAR/BORRAR globales.
    - El usuario puede EDITAR/BORRAR solo las suyas.
    """
    def has_object_permission(self, request, view, obj):
        # Métodos de lectura (GET, HEAD, OPTIONS) siempre permitidos
        if request.method in permissions.SAFE_METHODS:
            return True

        # Si es una categoría Global (usuario es None), BLOQUEAR escritura
        # (A menos que seas superuser, opcional)
        if obj.usuario is None:
            return False 

        # Si es privada, solo permitir si es el dueño
        return obj.usuario == request.user
    
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    - Los usuarios normales pueden VER (GET, HEAD, OPTIONS).
    - Solo los administradores (is_staff=True) pueden EDITAR (POST, PUT, DELETE).
    """
    def has_permission(self, request, view):
        # 1. Si es una operación segura (leer), dejamos pasar a cualquiera autenticado
        if request.method in permissions.SAFE_METHODS:
            return True

        # 2. Si quieren escribir/borrar, solo pasan si son Staff (Admin)
        return request.user and request.user.is_staff