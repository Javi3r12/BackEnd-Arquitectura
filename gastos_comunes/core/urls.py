from django.urls import path
from . import views  # Importar las vistas desde core

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('departamento/agregar/', views.agregar_departamento, name='agregar_departamento'),
    path('gastos/comunes/', views.generar_gastos_comunes, name='generar_gastos_comunes'),
    path('pago/marcar/', views.marcar_pago, name='marcar_pago'),
    path('gastos/pendientes/', views.gastos_pendientes, name='gastos_pendientes'),
]
