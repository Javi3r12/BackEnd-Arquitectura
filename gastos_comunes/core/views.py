from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime
import json
from .models import Departamento, GastoComun
from .utils import SistemaGastosComunes


def dashboard(request):
    return render(request, 'dashboard.html')

@csrf_exempt
def agregar_departamento(request):
    if request.method == "POST":
        numero = request.POST.get("numero")
        monto_diferenciado = request.POST.get("monto_diferenciado", None)
        if Departamento.objects.filter(numero=numero).exists():
            return HttpResponse("Error: El departamento ya existe.")
        Departamento.objects.create(numero=numero, monto_diferenciado=monto_diferenciado)
        return redirect("dashboard")
    return render(request, "agregar_departamento.html")

@csrf_exempt

def generar_gastos_comunes(request):
    if request.method == "POST":
        mes = request.POST.get("mes")
        anio = request.POST.get("anio")
        if mes and anio:
            resultado = SistemaGastosComunes().generar_gastos_comunes_mes(int(mes), int(anio))
        elif anio:
            resultado = SistemaGastosComunes().generar_gastos_comunes_anio(int(anio))
        else:
            return HttpResponse("Error: Debe proporcionar el mes y/o año.")
        return render(request, "generar_gastos_comunes.html", {"resultado": resultado})
    return render(request, "generar_gastos_comunes.html")

@csrf_exempt
def marcar_pago(request):
    if request.method == "POST":
        numero_departamento = request.POST.get("numero_departamento")
        mes = request.POST.get("mes")
        anio = request.POST.get("anio")
        fecha_pago = datetime.strptime(request.POST.get("fecha_pago"), "%Y-%m-%d")
        resultado = SistemaGastosComunes().marcar_pago(numero_departamento, int(mes), int(anio), fecha_pago)
        return render(request, "marcar_pago.html", {"resultado": resultado})
    return render(request, "marcar_pago.html")


def gastos_pendientes(request):
    gastos_pendientes = SistemaGastosComunes().obtener_gastos_pendientes(
        datetime.now().month, datetime.now().year
    )
    return render(request, "gastos_pendientes.html", {"gastos_pendientes": gastos_pendientes})


def dashboard(request):
    # Obtiene los gastos pendientes
    gastos_pendientes = GastoComun.objects.filter(pagado=False).values(
        'departamento__numero', 'periodo', 'monto'
    )
    # Prepara los datos de los gastos pendientes
    gastos_pendientes = [
        {
            "departamento": gasto["departamento__numero"],
            "periodo": gasto["periodo"],
            "monto": f"${gasto['monto']:,.0f} CLP"
        }
        for gasto in gastos_pendientes
    ]
    
    # Obtiene los departamentos
    departamentos = Departamento.objects.all().values('numero', 'monto_diferenciado')
    # Prepara los datos de los departamentos
    departamentos = [
        {
            "numero": dept["numero"],
            "monto_diferenciado": f"${dept['monto_diferenciado']:,.0f} CLP"
        }
        for dept in departamentos
    ]
    
    # Obtiene los gastos comunes generados
    gastos_comunes = GastoComun.objects.all().values('departamento__numero', 'monto', 'periodo')
    # Prepara los datos de los gastos comunes
    gastos_comunes = [
        {
            "departamento": gasto["departamento__numero"],
            "monto": f"${gasto['monto']:,.0f} CLP",
            "periodo": gasto["periodo"]
        }
        for gasto in gastos_comunes
    ]
    
    # Prepara los datos para pasar a la plantilla
    return render(request, 'dashboard.html', {
        "gastos_pendientes": gastos_pendientes,
        "departamentos": departamentos,
        "gastos_comunes": gastos_comunes
    })
