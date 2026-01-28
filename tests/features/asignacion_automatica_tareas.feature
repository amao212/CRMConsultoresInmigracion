# language:es
Característica: Asignación automática de tareas por tipo de trámite
  Como administrador del sistema
  quiero que las tareas se asignen automáticamente según el tipo de trámite
  para optimizar la carga de trabajo y reducir tiempos de procesamiento

  Antecedentes:
    Dado que existen los siguientes oficiales en el sistema
      | nombre          | rol      | estado     |
      | Juan Pérez      | Empleado | Activo     |
      | Ana Martínez    | Empleado | Activo     |
      | Carlos López    | Empleado | Activo     |
      | María García    | Empleado | Activo     |
      | Pedro Sánchez   | Empleado | Activo     |
      | Laura Torres    | Empleado | Inactivo   |

  Escenario: Asignar trámite automáticamente usando Round-Robin
    Dado que el último empleado asignado fue "Juan Pérez"
    Y se registra un nuevo trámite de modalidad "Estudio" con código "TRM-2026-201"
    Cuando el sistema ejecuta la asignación automática
    Entonces el trámite debe asignarse al siguiente oficial disponible "Ana Martínez"
    Y el registro de última asignación debe actualizarse a "Ana Martínez"

  Escenario: Asignar trámite cuando el siguiente oficial está inactivo
    Dado que el último empleado asignado fue "Pedro Sánchez"
    Y el siguiente oficial en la lista es "Laura Torres" pero está "Inactivo"
    Y se registra un nuevo trámite de modalidad "Trabajo" con código "TRM-2026-202"
    Cuando el sistema ejecuta la asignación automática
    Entonces el trámite debe asignarse al siguiente oficial activo "Juan Pérez" (reiniciando el ciclo)

  Escenario: Reasignar trámite manualmente a otro oficial
    Dado que el trámite "TRM-2026-200" está asignado al oficial "Juan Pérez"
    Cuando un administrador reasigna el trámite al oficial "María García"
    Entonces el trámite debe quedar asignado a "María García"
    Y el historial de cambios debe registrar la reasignación

#  Escenario: Crear tareas asociadas según el tipo de trámite (Funcionalidad futura)
#    Dado que se asigna el trámite "TRM-2026-200" de modalidad "Trabajo" al oficial "Juan Pérez"
#    Cuando el sistema crea las tareas asociadas
#    Entonces se deben crear las siguientes tareas
#      | tarea                              | etapa       | prioridad | plazo_dias |
#      | Verificar documentación inicial    | Recepción   | Normal    | 2          |
#      | Validar contrato de trabajo        | Evaluación  | Normal    | 5          |
#      | Verificar antecedentes             | Evaluación  | Alta      | 3          |
#      | Agendar entrevista                 | Entrevista  | Normal    | 7          |
#      | Revisar resultado de entrevista    | Entrevista  | Normal    | 1          |
#      | Emitir resolución                  | Aprobación  | Normal    | 3          |
#    Y cada tarea debe tener una fecha límite calculada
#    Y todas las tareas deben estar en estado "Pendiente"

#  Escenario: Notificar tareas próximas a vencer (Funcionalidad futura)
#    Dado que el oficial "Juan Pérez" tiene las siguientes tareas asignadas
#      | tarea                           | fecha_limite | estado    |
#      | Verificar documentación inicial | 2026-01-28   | Pendiente |
#      | Validar contrato de trabajo     | 2026-01-29   | Pendiente |
#      | Verificar antecedentes          | 2026-02-05   | Pendiente |
#    Y la fecha actual es "2026-01-27"
#    Cuando el sistema ejecuta el proceso de notificaciones diarias
#    Entonces se debe notificar al oficial "Juan Pérez"
#    Y la notificación debe incluir "1 tarea vence mañana"
#    Y la notificación debe incluir "1 tarea vence en 2 días"
#    Y las tareas deben marcarse con indicador visual de urgencia

#  Escenario: Marcar tarea como completada y avanzar trámite (Funcionalidad futura)
#    Dado que el oficial "Juan Pérez" tiene asignada la tarea "Verificar documentación inicial"
#    Y la tarea corresponde al trámite "TRM-2026-200"
#    Cuando el oficial marca la tarea como "Completada"
#    Y registra la observación "Documentación completa y verificada"
#    Entonces el estado de la tarea debe cambiar a "Completada"
#    Y se debe registrar la fecha y hora de finalización
#    Y si todas las tareas de la etapa están completadas
#    Entonces el trámite debe avanzar automáticamente a la siguiente etapa
#    Y se debe crear las tareas correspondientes a la nueva etapa
