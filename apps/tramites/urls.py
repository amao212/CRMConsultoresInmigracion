from django.urls import path
from .views import (
    GenerarFormularioPlantillaView, 
    IniciarTramiteView, 
    ActualizarTramiteView,
    DetalleTramiteSolicitanteView,
    DescargarPlantillaView,
    VisualizarPDFSolicitanteView,
    VisualizarDocumentoEspecificoView
)

app_name = 'tramites'

urlpatterns = [
    path('generar-formulario/<int:plantilla_id>/', GenerarFormularioPlantillaView.as_view(), name='generar_formulario_plantilla'),
    path('iniciar-tramite/<int:plantilla_id>/', IniciarTramiteView.as_view(), name='iniciar_tramite'),
    path('actualizar-tramite/<int:tramite_id>/', ActualizarTramiteView.as_view(), name='actualizar_tramite'),
    path('detalle/<int:tramite_id>/', DetalleTramiteSolicitanteView.as_view(), name='detalle_tramite'),
    path('descargar-plantilla/<int:tramite_id>/', DescargarPlantillaView.as_view(), name='descargar_plantilla'),
    path('tramite/<int:tramite_id>/pdf/', VisualizarPDFSolicitanteView.as_view(), name='visualizar-pdf'),
    path('documento/<int:documento_id>/ver/', VisualizarDocumentoEspecificoView.as_view(), name='visualizar-documento'),
]
