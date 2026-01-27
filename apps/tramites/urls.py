from django.urls import path
from .views import GenerarFormularioPlantillaView, IniciarTramiteView, ActualizarTramiteView

app_name = 'tramites'

urlpatterns = [
    path('generar-formulario/<int:plantilla_id>/', GenerarFormularioPlantillaView.as_view(), name='generar_formulario_plantilla'),
    path('iniciar-tramite/<int:plantilla_id>/', IniciarTramiteView.as_view(), name='iniciar_tramite'),
    path('actualizar-tramite/<int:tramite_id>/', ActualizarTramiteView.as_view(), name='actualizar_tramite'),
]
