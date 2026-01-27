"""
URLs para funcionalidades de empleados.
"""
from django.urls import path
from .views_empleado import (
    EmpleadoDashboardView,
    DetalleTramiteEmpleadoView,
    AprobarTramiteView,
    RechazarTramiteView,
    VisualizarPDFTramiteView,
    EstadoTramiteAPIView,
    HistorialGeneralView
)

app_name = 'empleado'

urlpatterns = [
    path('dashboard/', EmpleadoDashboardView.as_view(), name='dashboard'),
    path('tramites-asignados/', EmpleadoDashboardView.as_view(), name='tramites_asignados'),
    path('historial/', HistorialGeneralView.as_view(), name='historial_general'),
    path('tramite/<int:tramite_id>/', DetalleTramiteEmpleadoView.as_view(), name='detalle-tramite'),
    path('tramite/<int:tramite_id>/aprobar/', AprobarTramiteView.as_view(), name='aprobar-tramite'),
    path('tramite/<int:tramite_id>/rechazar/', RechazarTramiteView.as_view(), name='rechazar-tramite'),
    path('tramite/<int:tramite_id>/pdf/', VisualizarPDFTramiteView.as_view(), name='visualizar-pdf'),
    path('api/tramite/<int:tramite_id>/estado/', EstadoTramiteAPIView.as_view(), name='api-estado-tramite'),
]
