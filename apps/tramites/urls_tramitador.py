"""
URLs para funcionalidades de tramitadores.
"""
from django.urls import path
from .views_tramitador import (
    TramitadorDashboardView,
    DetalleTramiteTramitadorView,
    AprobarTramiteView,
    RechazarTramiteView,
    VisualizarPDFTramiteView,
    EstadoTramiteAPIView,
    HistorialGeneralView
)

app_name = 'tramitador'

urlpatterns = [
    path('dashboard/', TramitadorDashboardView.as_view(), name='dashboard'),
    path('tramites-asignados/', TramitadorDashboardView.as_view(), name='tramites_asignados'),
    path('historial/', HistorialGeneralView.as_view(), name='historial_general'),
    path('tramite/<int:tramite_id>/', DetalleTramiteTramitadorView.as_view(), name='detalle-tramite'),
    path('tramite/<int:tramite_id>/aprobar/', AprobarTramiteView.as_view(), name='aprobar-tramite'),
    path('tramite/<int:tramite_id>/rechazar/', RechazarTramiteView.as_view(), name='rechazar-tramite'),
    path('tramite/<int:tramite_id>/pdf/', VisualizarPDFTramiteView.as_view(), name='visualizar-pdf'),
    path('api/tramite/<int:tramite_id>/estado/', EstadoTramiteAPIView.as_view(), name='api-estado-tramite'),
]
