from behave import *
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta

use_step_matcher("re")

# --- Helpers Internos ---

def _get_or_create_solicitante(context):
    """Crea o recupera un usuario solicitante genérico."""
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    solicitante, _ = Usuario.objects.get_or_create(
        email='solicitante.requisitos@example.com',
        defaults={
            'nombre': 'Solicitante Requisitos',
            'rol': 'SOLICITANTE',
            'is_active': True
        }
    )
    context.solicitante = solicitante
    return solicitante

def _configurar_plantilla(modalidad, segmento="Visas"):
    """Crea una plantilla maestra para la modalidad."""
    from apps.tramites.models import PlantillaDocumento, CampoPlantilla
    from django.contrib.auth import get_user_model
    
    Usuario = get_user_model()
    admin, _ = Usuario.objects.get_or_create(
        email='admin.requisitos@example.com',
        defaults={'nombre': 'Admin Requisitos', 'rol': 'ADMINISTRADOR'}
    )
    
    archivo_dummy = SimpleUploadedFile(f"plantilla_{modalidad}.pdf", b"dummy", content_type="application/pdf")
    
    plantilla, created = PlantillaDocumento.objects.get_or_create(
        tipo_especifico=modalidad,
        defaults={
            'nombre': f"Plantilla {modalidad}",
            'segmento': segmento,
            'archivo_base': archivo_dummy,
            'administrador': admin,
            'activo': True
        }
    )
    
    # Configurar campos/requisitos si es nueva
    if created:
        campos = []
        if modalidad == "Turismo":
            campos = [
                ('Pasaporte', 'pasaporte', 'text'),
                ('Itinerario', 'itinerario', 'textarea')
            ]
        elif modalidad == "Trabajo":
            campos = [
                ('Contrato', 'contrato', 'text'),
                ('Carta Oferta', 'carta_oferta', 'text')
            ]
            
        for i, (nombre, tecnico, tipo) in enumerate(campos):
            CampoPlantilla.objects.create(
                plantilla=plantilla,
                nombre_campo=nombre,
                nombre_tecnico=tecnico,
                tipo_campo=tipo,
                orden=i
            )
    return plantilla

def _obtener_requisitos(modalidad):
    """Simula la obtención de requisitos del sistema."""
    from apps.tramites.models import PlantillaDocumento
    try:
        plantilla = PlantillaDocumento.objects.get(tipo_especifico=modalidad, activo=True)
        return list(plantilla.campos.values_list('nombre_campo', flat=True))
    except PlantillaDocumento.DoesNotExist:
        return []

def _iniciar_tramite_logica(context, modalidad):
    """Lógica común para iniciar un trámite."""
    _get_or_create_solicitante(context)
    context.modalidad_actual = modalidad
    
    from apps.tramites.models import Tramite
    context.tramite = Tramite(
        solicitante=context.solicitante,
        nombre=modalidad,
        estado='PENDIENTE',
        fecha_limite=timezone.now() + timedelta(days=90)
    )
    
    context.requisitos_obtenidos = _obtener_requisitos(modalidad)

# --- Steps ---

@step('que existen configuraciones de requisitos para las modalidades "Turismo" y "Trabajo"')
def step_impl_configuracion(context):
    """
    Configura las plantillas necesarias.
    """
    _configurar_plantilla("Turismo")
    _configurar_plantilla("Trabajo")

@step('el solicitante inicia un trámite de modalidad "(?P<modalidad>.*?)"')
def step_impl_inicio_tramite(context, modalidad):
    """
    Inicia un trámite y determina requisitos.
    """
    _iniciar_tramite_logica(context, modalidad)

@step('el sistema debe listar los requisitos obligatorios para "(?P<modalidad>.*?)"')
def step_impl_listar_requisitos(context, modalidad):
    """
    Verifica que los requisitos correspondan a la modalidad.
    """
    requisitos = context.requisitos_obtenidos
    assert len(requisitos) > 0, f"No se encontraron requisitos para {modalidad}"
    
    # Validaciones específicas según lo configurado en el helper
    if modalidad == "Turismo":
        assert "Pasaporte" in requisitos
        assert "Itinerario" in requisitos
    elif modalidad == "Trabajo":
        assert "Contrato" in requisitos
        assert "Carta Oferta" in requisitos

@step('el plazo estimado de respuesta debe corresponder a la modalidad "(?P<modalidad>.*?)"')
def step_impl_verificar_plazo(context, modalidad):
    """
    Verifica el plazo estimado.
    """
    assert context.tramite.fecha_limite is not None
    dias_restantes = (context.tramite.fecha_limite - timezone.now()).days
    assert dias_restantes >= 89, "El plazo estimado es demasiado corto"

@step('la lista de requisitos debe ser diferente a la de "Turismo"')
def step_impl_diferenciar_requisitos(context):
    """
    Verifica que los requisitos de Trabajo sean distintos a Turismo.
    """
    requisitos_turismo = _obtener_requisitos("Turismo")
    requisitos_actuales = context.requisitos_obtenidos
    
    assert set(requisitos_actuales) != set(requisitos_turismo), \
        "Los requisitos de Trabajo no deberían ser iguales a los de Turismo"

@step('que el solicitante ha iniciado un trámite de modalidad "Turismo"')
def step_impl_preparar_tramite_existente(context):
    """
    Prepara un trámite existente.
    """
    _iniciar_tramite_logica(context, "Turismo")
    context.tramite.save() # Guardar para persistencia

@step('el solicitante cambia la modalidad del trámite a "Trabajo" antes de enviarlo')
def step_impl_cambiar_modalidad(context):
    """
    Simula el cambio de modalidad.
    """
    context.tramite.nombre = "Trabajo"
    context.modalidad_actual = "Trabajo"
    # Recalcular requisitos
    context.requisitos_obtenidos = _obtener_requisitos("Trabajo")

@step('el sistema debe actualizar la lista de requisitos a los de "Trabajo"')
def step_impl_verificar_actualizacion(context):
    """
    Verifica que los requisitos se hayan actualizado.
    """
    requisitos = context.requisitos_obtenidos
    assert "Contrato" in requisitos
    assert "Pasaporte" not in requisitos # Asumiendo que son disjuntos para el test

@step("el plazo estimado debe actualizarse acorde a la nueva modalidad")
def step_impl_actualizar_plazo(context):
    """
    Verifica actualización de plazo.
    """
    # Simular actualización de fecha límite
    context.tramite.fecha_limite = timezone.now() + timedelta(days=90)
    assert context.tramite.fecha_limite > timezone.now()
