import json
from datetime import datetime

class Departamento:
    def __init__(self, numero):
        self.numero = numero
        self.gastos = {}  # Diccionario para almacenar los gastos por mes/año

    def agregar_gasto(self, gasto):
        # Añadir un gasto al departamento
        if gasto.periodo not in self.gastos:
            self.gastos[gasto.periodo] = gasto

    def obtener_gastos_pendientes(self, mes, anio):
        # Filtrar los gastos pendientes hasta el mes/año proporcionado
        pendientes = []
        for gasto in self.gastos.values():
            if gasto.pagado is False and gasto.fecha_pago is None:
                if gasto.periodo <= f"{mes}-{anio}":
                    pendientes.append(gasto)
        return pendientes

class GastoComun:
    def __init__(self, departamento, monto, periodo):
        self.departamento = departamento
        self.monto = monto
        self.periodo = periodo  # formato "MM-YYYY"
        self.pagado = False
        self.fecha_pago = None

    def pagar(self, fecha_pago):
        # Procesa el pago de un gasto
        if self.pagado:
            return "Pago duplicado"
        
        self.pagado = True
        self.fecha_pago = fecha_pago
        return self._estado_pago(fecha_pago)

    def _estado_pago(self, fecha_pago):
        # Determinar si el pago fue dentro o fuera del plazo
        fecha_pago_obj = datetime.strptime(fecha_pago, "%d-%m-%Y")
        fecha_periodo = datetime.strptime(f"01-{self.periodo}", "%d-%m-%Y")
        
        # El pago es a tiempo si la fecha de pago es antes del 5 del mes siguiente
        if fecha_pago_obj <= fecha_periodo.replace(day=5):
            return "Pago exitoso dentro del plazo"
        else:
            return "Pago exitoso fuera del plazo"
class GestionGastosComunes:
    def __init__(self):
        self.departamentos = {}  # Diccionario para almacenar los departamentos

    def agregar_departamento(self, numero_departamento):
        if numero_departamento not in self.departamentos:
            self.departamentos[numero_departamento] = Departamento(numero_departamento)

    def generar_gastos_comunes(self, tipo, mes, anio, monto_por_departamento=None):
        # Genera los gastos comunes por mes o por año
        if tipo == "mes":
            for dep in self.departamentos.values():
                gasto = GastoComun(dep.numero, monto_por_departamento, f"{mes}-{anio}")
                dep.agregar_gasto(gasto)
        elif tipo == "anio":
            for dep in self.departamentos.values():
                for m in range(1, 13):
                    periodo = f"{m:02d}-{anio}"
                    gasto = GastoComun(dep.numero, monto_por_departamento, periodo)
                    dep.agregar_gasto(gasto)

    def marcar_pago(self, numero_departamento, mes, anio, fecha_pago):
        # Marca un gasto como pagado
        dep = self.departamentos.get(numero_departamento)
        if not dep:
            return json.dumps({"error": "Departamento no encontrado"})

        periodo = f"{mes}-{anio}"
        gasto = dep.gastos.get(periodo)
        if not gasto:
            return json.dumps({"error": "Gasto no encontrado para el periodo indicado"})
        
        estado = gasto.pagar(fecha_pago)
        return json.dumps({
            "departamento": dep.numero,
            "fecha_pago": fecha_pago,
            "periodo": gasto.periodo,
            "estado": estado
        })
    
    def obtener_gastos_pendientes(self, mes, anio):
        # Obtener los gastos pendientes hasta el mes/año indicado
        resultado = []
        for dep in self.departamentos.values():
            pendientes = dep.obtener_gastos_pendientes(mes, anio)
            for gasto in pendientes:
                resultado.append({
                    "departamento": dep.numero,
                    "periodo": gasto.periodo,
                    "monto": gasto.monto
                })

        if not resultado:
            return json.dumps({"mensaje": "Sin montos pendientes"})

        # Ordenar por periodo
        resultado.sort(key=lambda x: x["periodo"])
        return json.dumps(resultado)

# Inicializamos el sistema


gestion = GestionGastosComunes()

# Agregar departamentos
gestion.agregar_departamento(1305)
gestion.agregar_departamento(1401)

# Generar gastos comunes para Octubre 2024
gestion.generar_gastos_comunes(tipo="mes", mes=10, anio=2024, monto_por_departamento=100)

# Marcar pago
pago_respuesta = gestion.marcar_pago(1305, 10, 2024, "03-11-2024")
print(pago_respuesta)

# Listar gastos pendientes hasta Octubre 2024
pendientes = gestion.obtener_gastos_pendientes(10, 2024)
print(pendientes)
