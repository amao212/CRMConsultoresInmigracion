from behave import *

use_step_matcher("re")


@step("que existen los siguientes oficiales en el sistema")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Dado que existen los siguientes oficiales en el sistema
                              | nombre | especialidad | carga_actual | max_tramites | estado |
                              | Juan
    Pérez | Trabajo | 8 | 15 | Disponible |
    | Ana
    Martínez | Estudio | 5 | 15 | Disponible |
    | Carlos
    López | Turismo | 12 | 15 | Disponible |
    | María
    García | Residencia | 3 | 10 | Disponible |
    | Pedro
    Sánchez | Trabajo | 14 | 15 | Disponible |
    | Laura
    Torres | Trabajo | 0 | 15 | De
    Vacaciones | ')


@step('que se registra un nuevo trámite de modalidad "Trabajo" con código "TRM-2026-200"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(
        u'STEP: Dado que se registra un nuevo trámite de modalidad "Trabajo" con código "TRM-2026-200"')


@step("el sistema ejecuta la asignación automática")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Cuando el sistema ejecuta la asignación automática')


@step('el trámite debe asignarse al oficial "María García"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces el trámite debe asignarse al oficial "María García"')


@step('la carga actual de "María García" debe incrementarse a 4')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y la carga actual de "María García" debe incrementarse a 4')


@step('se debe crear una tarea con prioridad "Normal"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y se debe crear una tarea con prioridad "Normal"')


@step("se debe notificar al oficial de la nueva asignación")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y se debe notificar al oficial de la nueva asignación')


@step('que se registra un nuevo trámite de modalidad "Estudio" con código "TRM-2026-201"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(
        u'STEP: Dado que se registra un nuevo trámite de modalidad "Estudio" con código "TRM-2026-201"')


@step('que se registra un nuevo trámite de modalidad "Trabajo" con código "TRM-2026-202"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(
        u'STEP: Dado que se registra un nuevo trámite de modalidad "Trabajo" con código "TRM-2026-202"')


@step('el trámite tiene la marca "Urgente"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y el trámite tiene la marca "Urgente"')


@step("se debe notificar al oficial con alerta de urgencia")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y se debe notificar al oficial con alerta de urgencia')


@step("el tiempo esperado de procesamiento debe reducirse en 50%")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y el tiempo esperado de procesamiento debe reducirse en 50%')


@step('que se asigna el trámite "TRM-2026-200" de modalidad "Trabajo" al oficial "Juan Pérez"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(
        u'STEP: Dado que se asigna el trámite "TRM-2026-200" de modalidad "Trabajo" al oficial "Juan Pérez"')


@step("el sistema crea las tareas asociadas")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Cuando el sistema crea las tareas asociadas')


@step("se deben crear las siguientes tareas")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces se deben crear las siguientes tareas
                              | tarea | etapa | prioridad | plazo_dias |
                              | Verificar
    documentación
    inicial | Recepción | Normal | 2 |
    | Validar
    contrato
    de
    trabajo | Evaluación | Normal | 5 |
    | Verificar
    antecedentes | Evaluación | Alta | 3 |
    | Agendar
    entrevista | Entrevista | Normal | 7 |
    | Revisar
    resultado
    de
    entrevista | Entrevista | Normal | 1 |
    | Emitir
    resolución | Aprobación | Normal | 3 | ')


@step("cada tarea debe tener una fecha límite calculada")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y cada tarea debe tener una fecha límite calculada')


@step('todas las tareas deben estar en estado "Pendiente"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y todas las tareas deben estar en estado "Pendiente"')


@step('que el oficial "Juan Pérez" tiene las siguientes tareas asignadas')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Dado que el oficial "Juan Pérez" tiene las siguientes tareas asignadas
                              | tarea | fecha_limite | estado |
                              | Verificar
    documentación
    inicial | 2026 - 01 - 28 | Pendiente |
    | Validar
    contrato
    de
    trabajo | 2026 - 01 - 29 | Pendiente |
    | Verificar
    antecedentes | 2026 - 02 - 05 | Pendiente | ')


@step('la fecha actual es "2026-01-27"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y la fecha actual es "2026-01-27"')


@step("el sistema ejecuta el proceso de notificaciones diarias")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Cuando el sistema ejecuta el proceso de notificaciones diarias')


@step('se debe notificar al oficial "Juan Pérez"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces se debe notificar al oficial "Juan Pérez"')


@step('la notificación debe incluir "1 tarea vence mañana"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y la notificación debe incluir "1 tarea vence mañana"')


@step("las tareas deben marcarse con indicador visual de urgencia")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y las tareas deben marcarse con indicador visual de urgencia')


@step('que el oficial "Juan Pérez" tiene asignada la tarea "Verificar documentación inicial"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(
        u'STEP: Dado que el oficial "Juan Pérez" tiene asignada la tarea "Verificar documentación inicial"')


@step('la tarea corresponde al trámite "TRM-2026-200"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y la tarea corresponde al trámite "TRM-2026-200"')


@step('el oficial marca la tarea como "Completada"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Cuando el oficial marca la tarea como "Completada"')


@step('registra la observación "Documentación completa y verificada"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y registra la observación "Documentación completa y verificada"')


@step('el estado de la tarea debe cambiar a "Completada"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces el estado de la tarea debe cambiar a "Completada"')


@step("se debe registrar la fecha y hora de finalización")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y se debe registrar la fecha y hora de finalización')


@step("si todas las tareas de la etapa están completadas")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y si todas las tareas de la etapa están completadas')


@step("el trámite debe avanzar automáticamente a la siguiente etapa")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces el trámite debe avanzar automáticamente a la siguiente etapa')


@step("se debe crear las tareas correspondientes a la nueva etapa")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y se debe crear las tareas correspondientes a la nueva etapa')