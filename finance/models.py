from django.db import models
from usuario.models import Usuario, Persona


class TipoDeuda(models.Model):
    id_tipo_deuda = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'tipo_deuda'

class Moneda(models.Model):
    id_moneda = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    simbolo = models.CharField(max_length=10)

    class Meta:
        db_table = 'moneda'

class Deuda(models.Model):
    id_deuda = models.AutoField(primary_key=True)
    persona = models.ForeignKey(Persona, on_delete=models.PROTECT)
    tipo_deuda = models.ForeignKey(TipoDeuda, on_delete=models.PROTECT)
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT)

    class Meta:
        db_table = 'deuda'

class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'categoria'

class DetalleDeuda(models.Model):
    id_detalle_deuda = models.AutoField(primary_key=True)
    deuda = models.ForeignKey(Deuda, on_delete=models.PROTECT)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'detalle_deuda'

class MetodoPago(models.Model):
    id_metodo_pago = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'metodo_pago'

class TipoTransaccion(models.Model):
    id_tipo_transaccion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'tipo_transaccion'

class Transaccion(models.Model):
    id_transaccion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    detalle_deuda = models.ForeignKey(DetalleDeuda, null=True, blank=True, on_delete=models.PROTECT)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    tipo_transaccion = models.ForeignKey(TipoTransaccion, on_delete=models.PROTECT)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'transaccion'