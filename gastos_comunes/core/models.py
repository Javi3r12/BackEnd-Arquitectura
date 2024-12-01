from django.db import models
from datetime import datetime, timedelta

class Departamento(models.Model):
    numero = models.IntegerField(unique=True)
    monto_diferenciado = models.IntegerField(default=200000)

    def __str__(self):
        return f"Departamento {self.numero}"

class GastoComun(models.Model):
    departamento = models.ForeignKey(Departamento, related_name='gastos', on_delete=models.CASCADE)
    periodo = models.CharField(max_length=7)  # Formato Año-Mes (Ej: "2024-11")
    monto = models.IntegerField()
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)

    def marcar_como_pagado(self, fecha_pago):
        if self.pagado:
            return "Pago duplicado"

        fecha_limite = datetime.strptime(self.periodo, "%Y-%m")
        ultimo_dia_mes = (fecha_limite.replace(month=fecha_limite.month % 12 + 1) - timedelta(days=1)).day
        fecha_limite = fecha_limite.replace(day=ultimo_dia_mes)

        estado_pago = "Pago exitoso dentro del plazo" if fecha_pago <= fecha_limite else "Pago exitoso fuera de plazo"
        
        self.pagado = True
        self.fecha_pago = fecha_pago
        self.save()
        return estado_pago
