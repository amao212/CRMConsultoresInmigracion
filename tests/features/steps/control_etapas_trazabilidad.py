from behave import *
from datetime import datetime, timedelta
from django.utils import timezone

use_step_matcher("re")

@step("que existen los siguientes estados de trámite en el sistema")
def step_impl(context):
    """
    Verifica que los estados definidos en el feature coincidan con los del modelo.
    No crea nada en BD porque son hardcoded en el modelo, pero valida consistencia.
    """
    from apps.tramites.models import Tramite
    
    estados_modelo = dict(Tramite.ESTADOS)
    for row in context.table:
        estado = row['estado']
        descripcion = row['descripcion']
        assert estado in estados_modelo, f"El estado {estado} no existe en el modelo Tramite"
        assert estados_modelo[estado] == descripcion, f"La descripción no coincide para {estado}"

@step('que un solicitante inicia un trámite de modalidad "(?P<modalidad>.*?)"')
def step_impl(context, modalidad):
    """
    Prepara el contexto para iniciar un trámite.
    Crea un solicitante de prueba.
    """
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    
    # Limpiar datos previos para aislamiento
    Usuario.objects.filter(email='solicitante.trazabilidad@example.com').delete()
    
    solicitante = Usuario.objects.create_user(
        email='solicitante.trazabilidad@example.com',
        password='password123',
        nombre='Solicitante Trazabilidad',
        rol='SOLICITANTE'
    )
    context.solicitante_actual = solicitante
    context.modalidad_actual = modalidad

@step('se registra el trámite con código "(?P<codigo>.*?)"')
def step_impl(context, codigo):
    """
    Crea el trámite en la base de datos de prueba.
    """
    from apps.tramites.models import Tramite
    
    # Limpiar trámites previos
    Tramite.objects.all().delete()
    
    tramite = Tramite.objects.create(
        solicitante=context.solicitante_actual,
        nombre=context.modalidad_actual,
        fecha_limite=timezone.now() + timedelta(days=90),
        estado='PENDIENTE' # Estado inicial por defecto
    )
    context.tramite_actual = tramite
    context.codigo_tramite = codigo

@step('el trámite debe iniciar en el estado "(?P<estado>.*?)"')
def step_impl(context, estado):
    """
    Verifica el estado inicial del trámite.
    """
    assert context.tramite_actual.estado == estado, \
        f"El estado inicial debería ser {estado}, pero es {context.tramite_actual.estado}"

@step('que el trámite "(?P<codigo>.*?)" tiene el siguiente historial')
def step_impl(context, codigo):
    """
    Crea un historial simulado para el trámite.
    """
    from apps.tramites.models import Tramite, HistorialCambios
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    
    # Crear solicitante y trámite si no existen (para soportar este step aislado)
    if not hasattr(context, 'tramite_actual'):
        solicitante, _ = Usuario.objects.get_or_create(
            email='solicitante.historial@example.com',
            defaults={'nombre': 'Solicitante Historial', 'rol': 'SOLICITANTE'}
        )
        tramite = Tramite.objects.create(
            solicitante=solicitante,
            nombre="Trámite Historial",
            fecha_limite=timezone.now() + timedelta(days=30),
            estado='PENDIENTE'
        )
        context.tramite_actual = tramite
    
    tramite = context.tramite_actual
    
    # Guardar la tabla en el contexto para validación posterior
    context.tabla_historial_esperada = context.table
    
    # Crear registros de historial
    for row in context.table:
        fecha_str = f"{row['fecha']} {row['hora']}"
        fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
        # Hacerlo timezone-aware para Django
        fecha_dt = timezone.make_aware(fecha_dt)
        
        usuario = None
        if row['oficial'] != 'Sistema':
            usuario, _ = Usuario.objects.get_or_create(
                email=f"{row['oficial'].lower().replace(' ', '.')}@example.com",
                defaults={'nombre': row['oficial'], 'rol': 'EMPLEADO'}
            )
            
        historial = HistorialCambios.objects.create(
            tramite=tramite,
            descripcion=row['descripcion'],
            usuario=usuario,
            estado_anterior=row['estado_anterior'],
            estado_nuevo=row['estado_nuevo']
        )
        # Forzar la fecha de creación (auto_now_add no se puede sobrescribir en create, hay que actualizar)
        historial.fecha_cambio = fecha_dt
        historial.save()

@step("el solicitante consulta el historial del trámite")
def step_impl(context):
    """
    Simula la consulta del historial.
    """
    tramite = context.tramite_actual
    # Obtener historial ordenado cronológicamente
    context.historial_consultado = tramite.historial.all().order_by('fecha_cambio')

@step("se debe mostrar el historial completo ordenado cronológicamente")
def step_impl(context):
    """
    Verifica que el historial consultado esté ordenado y completo.
    """
    historial = list(context.historial_consultado)
    assert len(historial) > 0, "El historial no debería estar vacío"
    
    # Verificar orden cronológico
    fechas = [h.fecha_cambio for h in historial]
    assert fechas == sorted(fechas), "El historial no está ordenado cronológicamente"
    
    # Verificar que coincida con la tabla del feature (si existe en el contexto)
    if hasattr(context, 'tabla_historial_esperada'):
        assert len(historial) == len(context.tabla_historial_esperada.rows), \
            f"Se esperaban {len(context.tabla_historial_esperada.rows)} registros, se encontraron {len(historial)}"

@step('que el trámite "(?P<codigo>.*?)" está en estado "(?P<estado>.*?)"')
def step_impl(context, codigo, estado):
    """
    Prepara un trámite en un estado específico para pruebas de transición.
    """
    from apps.tramites.models import Tramite
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    
    solicitante, _ = Usuario.objects.get_or_create(
        email='solicitante.estado@example.com',
        defaults={'nombre': 'Solicitante Estado', 'rol': 'SOLICITANTE'}
    )
    
    # Limpiar trámites previos
    Tramite.objects.all().delete()
    
    tramite = Tramite.objects.create(
        solicitante=solicitante,
        nombre="Trámite Estado",
        fecha_limite=timezone.now() + timedelta(days=30),
        estado=estado
    )
    context.tramite_actual = tramite
    context.codigo_tramite = codigo

@step("el oficial aprueba el trámite")
def step_impl(context):
    """
    Ejecuta la acción de aprobar el trámite usando el servicio.
    """
    from apps.tramites.services.aprobacion_service import AprobacionTramiteService
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    
    # Crear un oficial y asignarlo para poder aprobar
    oficial, _ = Usuario.objects.get_or_create(
        email='oficial.aprueba@example.com',
        defaults={'nombre': 'Oficial Aprueba', 'rol': 'EMPLEADO'}
    )
    
    tramite = context.tramite_actual
    tramite.empleado_asignado = oficial
    tramite.save()
    
    # Ejecutar aprobación
    AprobacionTramiteService.aprobar_tramite(tramite.id, oficial)
    tramite.refresh_from_db()

@step('el estado debe cambiar a "(?P<estado_esperado>.*?)"')
def step_impl(context, estado_esperado):
    """
    Verifica el cambio de estado.
    """
    assert context.tramite_actual.estado == estado_esperado, \
        f"El estado debería ser {estado_esperado}, pero es {context.tramite_actual.estado}"

@step("se debe registrar la fecha de aprobación")
def step_impl(context):
    """
    Verifica que se haya guardado la fecha de aprobación.
    """
    assert context.tramite_actual.fecha_aprobacion is not None, "La fecha de aprobación no se registró"

@step("el oficial rechaza el trámite")
def step_impl(context):
    """
    Prepara el contexto para el rechazo (necesita motivo en el siguiente paso).
    """
    # Solo preparamos el oficial, la acción real se hace cuando se tiene el motivo
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    
    oficial, _ = Usuario.objects.get_or_create(
        email='oficial.rechaza@example.com',
        defaults={'nombre': 'Oficial Rechaza', 'rol': 'EMPLEADO'}
    )
    
    tramite = context.tramite_actual
    tramite.empleado_asignado = oficial
    tramite.save()
    context.oficial_actual = oficial

@step('registra el motivo "(?P<motivo>.*?)"')
def step_impl(context, motivo):
    """
    Ejecuta la acción de rechazar con el motivo dado.
    """
    from apps.tramites.services.aprobacion_service import AprobacionTramiteService
    
    AprobacionTramiteService.rechazar_tramite(
        context.tramite_actual.id, 
        context.oficial_actual, 
        motivo
    )
    context.tramite_actual.refresh_from_db()

@step("se debe registrar la fecha de rechazo")
def step_impl(context):
    """
    Verifica que se haya guardado la fecha de rechazo.
    """
    assert context.tramite_actual.fecha_rechazo is not None, "La fecha de rechazo no se registró"

@step("se debe registrar el motivo del rechazo")
def step_impl(context):
    """
    Verifica que se haya guardado el motivo de rechazo.
    """
    assert context.tramite_actual.motivo_rechazo is not None, "El motivo de rechazo no se registró"
    assert len(context.tramite_actual.motivo_rechazo) > 0, "El motivo de rechazo está vacío"
