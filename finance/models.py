from django.db import models
from usuario.models import Usuario, Persona


class TipoMovimiento(models.Model):
    id_tipo_movimiento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'tipo_movimiento'

class Moneda(models.Model):
    id_moneda = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    simbolo = models.CharField(max_length=10)

    class Meta:
        db_table = 'moneda'

class CuentaCorriente(models.Model):
    id_cuenta_corriente = models.AutoField(primary_key=True)
    persona = models.ForeignKey(Persona, on_delete=models.PROTECT)
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cuenta_corriente'

class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(Usuario,null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        db_table = 'categoria'

class MovimientoCuenta(models.Model):
    id_movimiento_cuenta = models.AutoField(primary_key=True)
    cuenta_corriente = models.ForeignKey(CuentaCorriente, on_delete=models.PROTECT)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    tipo_movimiento = models.ForeignKey(TipoMovimiento, on_delete=models.PROTECT)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    monto_inicial = models.DecimalField(max_digits=100, decimal_places=2, default= 0)
    saldo_pendiente = models.DecimalField(max_digits=100, decimal_places=2, default = monto_inicial)

    def save(self, *args, **kwargs):
        # Si el objeto no tiene ID (es decir, es nuevo y se está creando por primera vez)
        if not self.pk:
            # El saldo pendiente inicial será exactamente igual al monto prestado
            self.saldo_pendiente = self.monto_inicial
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = 'movimiento_cuenta'

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
    movimiento_cuenta = models.ForeignKey(MovimientoCuenta, null=True, blank=True, on_delete=models.PROTECT)
    persona = models.ForeignKey(Persona, null=True, blank=True, on_delete=models.PROTECT)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    tipo_transaccion = models.ForeignKey(TipoTransaccion, on_delete=models.PROTECT)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=100, decimal_places=2)
    
    class Meta:
        db_table = 'transaccion'