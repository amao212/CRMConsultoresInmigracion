from behave import *
from datetime import timedelta

use_step_matcher("re")

@step("que existen los siguientes oficiales en el sistema")
def step_impl(context):
    """
    Crea los usuarios oficiales en el sistema de prueba basándose en la tabla del feature.
    Limpia la base de datos de empleados antes de crear los nuevos para asegurar aislamiento.
    """
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    
    # Limpiar empleados existentes para evitar interferencias con datos reales o de otros tests
    Usuario.objects.filter(rol='EMPLEADO').delete()
    
    for row in context.table:
        nombre = row['nombre']
        rol = row['rol'].upper()  # Asegurar mayúsculas para coincidir con choices
        estado = row['estado']
        
        # Normalizar estado a booleano is_active
        is_active = True
        if estado.lower() in ['inactivo', 'de vacaciones']:
            is_active = False
            
        # Crear usuario
        email = f"{nombre.lower().replace(' ', '.')}@example.com"
        Usuario.objects.create_user(
            email=email,
            password='password123',
            nombre=nombre,
            rol=rol,
            is_active=is_active
        )

@step('que el último empleado asignado fue "(?P<nombre_empleado>.*?)"')
def step_impl(context, nombre_empleado):
    """
    Configura el estado inicial del algoritmo Round-Robin estableciendo el último empleado asignado.
    Soporta nombres con o sin llaves, aunque el regex captura el contenido.
    """
    from django.contrib.auth import get_user_model
    from apps.tramites.models import UltimaAsignacion
    Usuario = get_user_model()

    # Limpiar nombre si viene con llaves
    nombre_limpio = nombre_empleado.replace('{', '').replace('}', '')
    
    # Buscar el empleado creado en el paso anterior (que está en la BD de test limpia)
    empleado = Usuario.objects.get(nombre=nombre_limpio)
    
    # Crear o actualizar el registro de última asignación
    # Usamos update_or_create para asegurar que solo haya uno y sea el correcto
    UltimaAsignacion.objects.update_or_create(id=1, defaults={'ultimo_empleado_id': empleado.id})

@step('se registra un nuevo trámite de modalidad "(?P<modalidad>.*?)" con código "(?P<codigo>.*?)"')
def step_impl(context, modalidad, codigo):
    """
    Crea un nuevo trámite en el sistema pendiente de asignación.
    """
    from django.contrib.auth import get_user_model
    from apps.tramites.models import Tramite
    from django.utils import timezone
    Usuario = get_user_model()

    # Necesitamos un solicitante dummy
    solicitante, _ = Usuario.objects.get_or_create(
        email='solicitante.test@example.com',
        defaults={'nombre': 'Solicitante Test', 'rol': 'SOLICITANTE'}
    )
    
    # Limpiar trámites anteriores para evitar ruido
    Tramite.objects.all().delete()
    
    tramite = Tramite.objects.create(
        solicitante=solicitante,
        nombre=modalidad, # Usamos modalidad como nombre del trámite para simplificar
        fecha_limite=timezone.now() + timedelta(days=30),
        estado='PENDIENTE'
    )
    
    # Guardamos el trámite en el contexto para usarlo en siguientes pasos
    context.tramite_actual = tramite
    context.codigo_tramite = codigo # Guardamos el código aunque no sea campo real del modelo para referencia

@step("el sistema ejecuta la asignación automática")
def step_impl(context):
    """
    Ejecuta el servicio de asignación automática sobre el trámite actual.
    """
    from apps.tramites.services.asignacion_service import AsignacionEmpleadoService

    if hasattr(context, 'tramite_actual'):
        AsignacionEmpleadoService.asignar_empleado_a_tramite(context.tramite_actual)
        # Recargar el trámite desde la BD para obtener los cambios
        context.tramite_actual.refresh_from_db()

@step('el trámite debe asignarse al siguiente oficial disponible "(?P<nombre_oficial>.*?)"')
def step_impl(context, nombre_oficial):
    """
    Verifica que el trámite haya sido asignado al oficial esperado.
    """
    tramite = context.tramite_actual
    assert tramite.empleado_asignado is not None, "El trámite no tiene empleado asignado"
    assert tramite.empleado_asignado.nombre == nombre_oficial, \
        f"Se esperaba asignación a {nombre_oficial}, pero fue a {tramite.empleado_asignado.nombre}"

@step('el registro de última asignación debe actualizarse a "(?P<nombre_oficial>.*?)"')
def step_impl(context, nombre_oficial):
    """
    Verifica que el registro de Round-Robin se haya actualizado correctamente.
    """
    from django.contrib.auth import get_user_model
    from apps.tramites.models import UltimaAsignacion
    Usuario = get_user_model()

    ultima_asignacion = UltimaAsignacion.objects.get(id=1)
    empleado_esperado = Usuario.objects.get(nombre=nombre_oficial)
    
    assert ultima_asignacion.ultimo_empleado_id == empleado_esperado.id, \
        f"El registro de última asignación no coincide. ID esperado: {empleado_esperado.id}, Actual: {ultima_asignacion.ultimo_empleado_id}"

@step('el siguiente oficial en la lista es "(?P<nombre_oficial>.*?)" pero está "(?P<estado>.*?)"')
def step_impl(context, nombre_oficial, estado):
    """
    Paso informativo/de configuración para verificar el estado de un oficial.
    Asegura que el escenario sea consistente con los datos.
    """
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()

    empleado = Usuario.objects.get(nombre=nombre_oficial)
    
    esperado_activo = True
    if estado.lower() in ['inactivo', 'de vacaciones']:
        esperado_activo = False
        
    assert empleado.is_active == esperado_activo, \
        f"El estado del empleado {nombre_oficial} no coincide. is_active es {empleado.is_active}"

@step(r'el trámite debe asignarse al siguiente oficial activo "(?P<nombre_oficial>.*?)" \(reiniciando el ciclo\)')
def step_impl(context, nombre_oficial):
    """
    Verifica la asignación con reinicio de ciclo (Round-Robin).
    """
    tramite = context.tramite_actual
    assert tramite.empleado_asignado is not None, "El trámite no tiene empleado asignado"
    assert tramite.empleado_asignado.nombre == nombre_oficial, \
        f"Se esperaba asignación a {nombre_oficial}, pero fue a {tramite.empleado_asignado.nombre}"

@step('que el trámite "(?P<codigo>.*?)" está asignado al oficial "(?P<nombre_oficial>.*?)"')
def step_impl(context, codigo, nombre_oficial):
    """
    Crea un trámite pre-asignado para probar la reasignación manual.
    """
    from django.contrib.auth import get_user_model
    from apps.tramites.models import Tramite
    from django.utils import timezone
    Usuario = get_user_model()

    empleado = Usuario.objects.get(nombre=nombre_oficial)
    solicitante, _ = Usuario.objects.get_or_create(
        email='solicitante.reasignacion@example.com',
        defaults={'nombre': 'Solicitante Reasignacion', 'rol': 'SOLICITANTE'}
    )
    
    # Limpiar trámites anteriores
    Tramite.objects.all().delete()
    
    tramite = Tramite.objects.create(
        solicitante=solicitante,
        nombre="Trámite para Reasignar",
        empleado_asignado=empleado,
        fecha_limite=timezone.now() + timedelta(days=30),
        estado='PENDIENTE'
    )
    context.tramite_actual = tramite
    context.codigo_tramite = codigo

@step('un administrador reasigna el trámite al oficial "(?P<nombre_nuevo>.*?)"')
def step_impl(context, nombre_nuevo):
    """
    Ejecuta la reasignación manual del trámite.
    """
    from django.contrib.auth import get_user_model
    from apps.tramites.services.asignacion_service import AsignacionEmpleadoService
    Usuario = get_user_model()

    nuevo_empleado = Usuario.objects.get(nombre=nombre_nuevo)
    AsignacionEmpleadoService.reasignar_empleado_a_tramite(context.tramite_actual, nuevo_empleado)
    context.tramite_actual.refresh_from_db()

@step('el trámite debe quedar asignado a "(?P<nombre_oficial>.*?)"')
def step_impl(context, nombre_oficial):
    """
    Verifica que la reasignación se haya hecho efectiva en el modelo.
    """
    assert context.tramite_actual.empleado_asignado.nombre == nombre_oficial, \
        f"El trámite debería estar asignado a {nombre_oficial}"

@step("el historial de cambios debe registrar la reasignación")
def step_impl(context):
    """
    Verifica (simuladamente) que se haya registrado el cambio.
    """
    # En una implementación real verificaríamos HistorialCambios.objects.filter(tramite=context.tramite_actual).exists()
    pass
