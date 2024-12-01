from .models import Departamento, GastoComun
from datetime import datetime, timedelta

class SistemaGastosComunes:
    def agregar_departamento(self, numero, monto_diferenciado=None):
        if Departamento.objects.filter(numero=numero).exists():
            return {"error": "El departamento ya existe."}
        Departamento.objects.create(numero=numero, monto_diferenciado=monto_diferenciado)
        return {"mensaje": f"Departamento {numero} agregado."}

    def generar_gastos_comunes_mes(self, mes, anio):
        gastos_generados = []
        periodo = f"{anio}-{mes:02d}"
        departamentos = Departamento.objects.all()
        for depto in departamentos:
            if not GastoComun.objects.filter(departamento=depto, periodo=periodo).exists():
                gasto = GastoComun.objects.create(
                    departamento=depto,
                    periodo=periodo,
                    monto=depto.monto_diferenciado
                )
                gastos_generados.append({
                    "departamento": depto.numero,
                    "periodo": periodo,
                    "monto": f"${gasto.monto:,.0f} CLP"
                })
        return {
            "accion": "Listado de gastos generados",
            "mes": f"{mes}",
            "año": anio,
            "gastos_generados": gastos_generados
        }

    def generar_gastos_comunes_anio(self, anio):
        gastos_generados = []
        for mes in range(1, 13):
            resultado_mes = self.generar_gastos_comunes_mes(mes, anio)
            gastos_generados.extend(resultado_mes["gastos_generados"])
        return {
            "accion": "Listado de gastos generados",
            "año": anio,
            "gastos_generados": gastos_generados
        }

    def marcar_pago(self, numero_departamento, mes, anio, fecha_pago):
        departamento = Departamento.objects.filter(numero=numero_departamento).first()
        if not departamento:
            return {"error": "Departamento no encontrado"}
        periodo = f"{anio}-{mes:02d}"
        gasto = GastoComun.objects.filter(departamento=departamento, periodo=periodo, pagado=False).first()
        if gasto:
            fecha_limite = datetime.strptime(periodo, "%Y-%m")
            ultimo_dia_mes = (fecha_limite.replace(month=fecha_limite.month % 12 + 1) - timedelta(days=1)).day
            fecha_limite = fecha_limite.replace(day=ultimo_dia_mes)
            estado_pago = (
                "Pago exitoso dentro del plazo"
                if fecha_pago <= fecha_limite else
                "Pago exitoso fuera de plazo"
            )
            gasto.pagado = True
            gasto.fecha_pago = fecha_pago
            gasto.save()
            return {
                "departamento": numero_departamento,
                "fecha_pago": fecha_pago.strftime('%Y-%m-%d'),
                "periodo": periodo,
                "estado_pago": estado_pago
            }
        return {"error": "Gasto no encontrado o ya pagado"}

    def obtener_gastos_pendientes(self, mes, anio):
        gastos_pendientes = GastoComun.objects.filter(
            pagado=False,
            periodo__lte=f"{anio}-{mes:02d}"
        )
        if gastos_pendientes:
            return {
                "accion": "Listado de gastos pendientes",
                "mes": f"{mes}",
                "año": anio,
                "gastos_pendientes": [
                    {
                        "departamento": gasto.departamento.numero,
                        "periodo": gasto.periodo,
                        "monto": f"${gasto.monto:,.0f} CLP"
                    }
                    for gasto in gastos_pendientes
                ]
            }
        return {
            "accion": "Listado de gastos pendientes",
            "mes": f"{mes}",
            "año": anio,
            "gastos_pendientes": "Sin montos pendientes"
        }
