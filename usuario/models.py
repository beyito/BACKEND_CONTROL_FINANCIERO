from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class Usuario(AbstractUser):
    fecha_nacimiento = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'usuario'

class Persona(models.Model):
    id_persona = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=100)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'persona'