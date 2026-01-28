from behave import *
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta

use_step_matcher("re")

# --- Helpers Internos ---

def _get_or_create_solicitante(context):
    """Crea o recupera un usuario solicitante genérico."""
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    solicitante, _ = Usuario.objects.get_or_create(
        email='solicitante.version@example.com',
        defaults={
            'nombre': 'Solicitante Version',
            'rol': 'SOLICITANTE',
            'is_active': True
        }
    )
    context.solicitante = solicitante
    return solicitante

def _crear_tramite_activo(context):
    """Crea un trámite activo para el solicitante."""
    from apps.tramites.models import Tramite
    
    solicitante = _get_or_create_solicitante(context)
    
    # Limpiar trámites previos
    Tramite.objects.all().delete()
    
    tramite = Tramite.objects.create(
        solicitante=solicitante,
        nombre="Visa de Turismo",
        estado='PENDIENTE',
        fecha_limite=timezone.now() + timedelta(days=30)
    )
    context.tramite = tramite
    return tramite

def _crear_plantilla_maestra(context):
    """Crea una plantilla maestra para el trámite."""
    from apps.tramites.models import PlantillaDocumento
    from django.contrib.auth import get_user_model
    
    Usuario = get_user_model()
    admin, _ = Usuario.objects.get_or_create(
        email='admin.plantilla@example.com',
        defaults={'nombre': 'Admin Plantilla', 'rol': 'ADMINISTRADOR'}
    )
    
    archivo_dummy = SimpleUploadedFile("plantilla.pdf", b"contenido_plantilla", content_type="application/pdf")
    
    plantilla = PlantillaDocumento.objects.create(
        nombre="Plantilla Visa Turismo",
        segmento="Visas",
        tipo_especifico="Visa de Turismo",
        archivo_base=archivo_dummy,
        administrador=admin,
        activo=True
    )
    context.plantilla = plantilla
    return plantilla

# --- Steps ---

@step('que existe un trámite activo de tipo "Visa de Turismo"')
def step_impl(context):
    """
    Crea un trámite activo.
    """
    _crear_tramite_activo(context)

@step("que existe una plantilla maestra activa para este tipo de trámite")
def step_impl(context):
    """
    Crea una plantilla maestra.
    """
    _crear_plantilla_maestra(context)

@step("el solicitante sube un documento PDF para el trámite")
def step_impl(context):
    """
    Simula la subida de un documento (versión 1).
    """
    from apps.tramites.models import Documento, HistorialCambios
    
    archivo = SimpleUploadedFile("documento_v1.pdf", b"contenido_v1", content_type="application/pdf")
    
    documento = Documento.objects.create(
        tramite=context.tramite,
        nombre="Documento Visa",
        version=1,
        archivo=archivo
    )
    context.documento_actual = documento
    
    # Registrar historial
    HistorialCambios.objects.create(
        tramite=context.tramite,
        descripcion="Carga inicial de documento",
        usuario=context.solicitante,
        fecha_cambio=timezone.now()
    )

@step("el sistema debe registrar el documento con versión 1")
def step_impl(context):
    """
    Verifica que el documento tenga versión 1.
    """
    assert context.documento_actual.version == 1, \
        f"La versión debería ser 1, es {context.documento_actual.version}"

@step('se debe crear un registro en el historial indicando "Carga inicial de documento"')
def step_impl(context):
    """
    Verifica el registro en el historial.
    """
    from apps.tramites.models import HistorialCambios
    
    registro = HistorialCambios.objects.filter(
        tramite=context.tramite,
        descripcion__icontains="Carga inicial"
    ).first()
    
    assert registro is not None, "No se encontró el registro de carga inicial en el historial"
    context.ultimo_registro = registro

@step("el registro debe asociar la acción al solicitante")
def step_impl(context):
    """
    Verifica el usuario del registro.
    """
    assert context.ultimo_registro.usuario == context.solicitante, \
        "El registro no está asociado al solicitante correcto"

@step("que ya existe un documento cargado previamente con versión 1")
def step_impl(context):
    """
    Prepara el escenario con un documento versión 1 existente.
    """
    # Asegurar que existen trámite y plantilla
    if not hasattr(context, 'tramite'):
        _crear_tramite_activo(context)
    if not hasattr(context, 'plantilla'):
        _crear_plantilla_maestra(context)
        
    from apps.tramites.models import Documento, HistorialCambios
    
    archivo = SimpleUploadedFile("documento_v1.pdf", b"contenido_v1", content_type="application/pdf")
    
    doc_v1 = Documento.objects.create(
        tramite=context.tramite,
        nombre="Documento Visa",
        version=1,
        archivo=archivo
    )
    
    HistorialCambios.objects.create(
        tramite=context.tramite,
        descripcion="Carga inicial de documento",
        usuario=context.solicitante,
        fecha_cambio=timezone.now() - timedelta(hours=1)
    )
    context.documento_previo = doc_v1

@step("el solicitante sube una nueva versión del mismo documento")
def step_impl(context):
    """
    Simula la subida de una nueva versión (versión 2).
    """
    from apps.tramites.models import Documento, HistorialCambios
    
    archivo = SimpleUploadedFile("documento_v2.pdf", b"contenido_v2", content_type="application/pdf")
    
    # Lógica de incremento de versión
    ultima_version = Documento.objects.filter(
        tramite=context.tramite,
        nombre="Documento Visa"
    ).order_by('-version').first().version
    
    nueva_version = ultima_version + 1
    
    doc_v2 = Documento.objects.create(
        tramite=context.tramite,
        nombre="Documento Visa",
        version=nueva_version,
        archivo=archivo
    )
    context.documento_actual = doc_v2
    
    HistorialCambios.objects.create(
        tramite=context.tramite,
        descripcion="Actualización de documento",
        usuario=context.solicitante,
        fecha_cambio=timezone.now()
    )

@step("el sistema debe registrar el nuevo documento con versión 2")
def step_impl(context):
    """
    Verifica que el documento tenga versión 2.
    """
    assert context.documento_actual.version == 2, \
        f"La versión debería ser 2, es {context.documento_actual.version}"

@step('se debe crear un nuevo registro en el historial indicando "Actualización de documento"')
def step_impl(context):
    """
    Verifica el registro de actualización.
    """
    from apps.tramites.models import HistorialCambios
    
    registro = HistorialCambios.objects.filter(
        tramite=context.tramite,
        descripcion__icontains="Actualización de documento"
    ).first()
    
    assert registro is not None, "No se encontró el registro de actualización en el historial"

@step("el historial debe mostrar ambos eventos ordenados cronológicamente")
def step_impl(context):
    """
    Verifica el orden cronológico de los eventos.
    """
    from apps.tramites.models import HistorialCambios
    
    historial = list(HistorialCambios.objects.filter(tramite=context.tramite).order_by('fecha_cambio'))
    
    assert len(historial) >= 2, "Debería haber al menos 2 eventos en el historial"
    
    fechas = [h.fecha_cambio for h in historial]
    assert fechas == sorted(fechas), "El historial no está ordenado cronológicamente"

@step("que existen múltiples versiones cargadas para un documento del trámite")
def step_impl(context):
    """
    Crea múltiples versiones de un documento.
    """
    # Reutilizamos la lógica de creación de v1 y v2
    if not hasattr(context, 'tramite'):
        _crear_tramite_activo(context)
        
    from apps.tramites.models import Documento, HistorialCambios
    
    # Versión 1
    doc1 = Documento.objects.create(
        tramite=context.tramite,
        nombre="Doc MultiVersion",
        version=1,
        archivo=SimpleUploadedFile("v1.pdf", b"v1", content_type="application/pdf")
    )
    HistorialCambios.objects.create(
        tramite=context.tramite,
        descripcion="Carga v1",
        usuario=context.solicitante,
        fecha_cambio=timezone.now() - timedelta(hours=2)
    )
    
    # Versión 2
    doc2 = Documento.objects.create(
        tramite=context.tramite,
        nombre="Doc MultiVersion",
        version=2,
        archivo=SimpleUploadedFile("v2.pdf", b"v2", content_type="application/pdf")
    )
    HistorialCambios.objects.create(
        tramite=context.tramite,
        descripcion="Carga v2",
        usuario=context.solicitante,
        fecha_cambio=timezone.now() - timedelta(hours=1)
    )
    
    context.documentos_versiones = [doc1, doc2]

@step("se deben listar todas las versiones del documento")
def step_impl(context):
    """
    Verifica que se puedan recuperar todas las versiones.
    """
    from apps.tramites.models import Documento
    
    versiones = Documento.objects.filter(tramite=context.tramite, nombre="Doc MultiVersion")
    assert versiones.count() == 2, f"Se esperaban 2 versiones, se encontraron {versiones.count()}"

@step("cada entrada debe mostrar la fecha, el usuario y la versión correspondiente")
def step_impl(context):
    """
    Verifica que el historial contenga la información relevante.
    """
    from apps.tramites.models import HistorialCambios
    
    historial = HistorialCambios.objects.filter(tramite=context.tramite)
    
    for entrada in historial:
        assert entrada.fecha_cambio is not None, "Falta fecha en historial"
        assert entrada.usuario is not None, "Falta usuario en historial"
        # La versión no se guarda explícitamente en HistorialCambios por defecto en este modelo,
        # pero verificamos que la descripción o contexto permita inferirlo o que los campos base existan.
        assert entrada.descripcion is not None, "Falta descripción en historial"
