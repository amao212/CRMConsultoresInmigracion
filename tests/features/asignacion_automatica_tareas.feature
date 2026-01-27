# language:es
Característica: Asignación automática de tareas por tipo de trámite
  Como administrador del sistema
  quiero que las tareas se asignen automáticamente según el tipo de trámite
  para optimizar la carga de trabajo y reducir tiempos de procesamiento

  Antecedentes:
    Dado que existen los siguientes oficiales en el sistema
      | nombre          | especialidad        | carga_actual | max_tramites | estado     |
      | Juan Pérez      | Trabajo             | 8            | 15           | Disponible |
      | Ana Martínez    | Estudio             | 5            | 15           | Disponible |
      | Carlos López    | Turismo             | 12           | 15           | Disponible |
      | María García    | Residencia          | 3            | 10           | Disponible |
      | Pedro Sánchez   | Trabajo             | 14           | 15           | Disponible |
      | Laura Torres    | Trabajo             | 0            | 15           | De Vacaciones |

  Escenario: Asignar trámite de trabajo al oficial con menor carga
    Dado que se registra un nuevo trámite de modalidad "Trabajo" con código "TRM-2026-200"
    Cuando el sistema ejecuta la asignación automática
    Entonces el trámite debe asignarse al oficial "María García"
    Y la carga actual de "María García" debe incrementarse a 4
    Y se debe crear una tarea con prioridad "Normal"
    Y se debe notificar al oficial de la nueva asignación

  Escenario: Asignar trámite de estudio al único oficial especializado
    Dado que se registra un nuevo trámite de modalidad "Estudio" con código "TRM-2026-201"
    Cuando el sistema ejecuta la asignación automática
    Entonces el trámite debe asignarse al oficial "Ana Martínez"
    Y la carga actual de "Ana Martínez" debe incrementarse a 6
    Y se debe crear una tarea con prioridad "Normal"

  Escenario: Asignar trámite urgente con alta prioridad
    Dado que se registra un nuevo trámite de modalidad "Trabajo" con código "TRM-2026-202"
    Y el trámite tiene la marca "Urgente"
    Cuando el sistema ejecuta la asignación automática
    Entonces el trámite debe asignarse al oficial "Juan Pérez"
    Y se debe crear una tarea con prioridad "Alta"
    Y se debe notificar al oficial con alerta de urgencia
    Y el tiempo esperado de procesamiento debe reducirse en 50%

#  Escenario: No asignar cuando todos los oficiales están al máximo de capacidad
#    Dado que todos los oficiales especializados en "Trabajo" tienen su carga máxima
#      | nombre          | carga_actual | max_tramites |
#      | Juan Pérez      | 15           | 15           |
#      | Pedro Sánchez   | 15           | 15           |
#      | María García    | 10           | 10           |
#    Y se registra un nuevo trámite de modalidad "Trabajo" con código "TRM-2026-203"
#    Cuando el sistema intenta ejecutar la asignación automática
#    Entonces el trámite debe quedar en estado "En Cola"
#    Y se debe agregar a la cola de asignación pendiente
#    Y se debe notificar al administrador de la sobrecarga
#    Y se debe calcular el tiempo estimado de espera

#  Escenario: Reasignar automáticamente cuando un oficial está de vacaciones
#    Dado que el oficial "Laura Torres" tiene 5 trámites asignados
#    Y el oficial "Laura Torres" marca su estado como "De Vacaciones"
#    Cuando el sistema detecta el cambio de estado
#    Entonces los 5 trámites deben reasignarse automáticamente
#    Y se debe aplicar el algoritmo de balanceo de carga
#    Y se debe notificar a los nuevos oficiales asignados
#    Y se debe registrar el motivo de reasignación "Oficial de vacaciones"

  Escenario: Crear tareas asociadas según el tipo de trámite
    Dado que se asigna el trámite "TRM-2026-200" de modalidad "Trabajo" al oficial "Juan Pérez"
    Cuando el sistema crea las tareas asociadas
    Entonces se deben crear las siguientes tareas
      | tarea                              | etapa       | prioridad | plazo_dias |
      | Verificar documentación inicial    | Recepción   | Normal    | 2          |
      | Validar contrato de trabajo        | Evaluación  | Normal    | 5          |
      | Verificar antecedentes             | Evaluación  | Alta      | 3          |
      | Agendar entrevista                 | Entrevista  | Normal    | 7          |
      | Revisar resultado de entrevista    | Entrevista  | Normal    | 1          |
      | Emitir resolución                  | Aprobación  | Normal    | 3          |
    Y cada tarea debe tener una fecha límite calculada
    Y todas las tareas deben estar en estado "Pendiente"

  Escenario: Notificar tareas próximas a vencer
    Dado que el oficial "Juan Pérez" tiene las siguientes tareas asignadas
      | tarea                           | fecha_limite | estado    |
      | Verificar documentación inicial | 2026-01-28   | Pendiente |
      | Validar contrato de trabajo     | 2026-01-29   | Pendiente |
      | Verificar antecedentes          | 2026-02-05   | Pendiente |
    Y la fecha actual es "2026-01-27"
    Cuando el sistema ejecuta el proceso de notificaciones diarias
    Entonces se debe notificar al oficial "Juan Pérez"
    Y la notificación debe incluir "1 tarea vence mañana"
    Y la notificación debe incluir "1 tarea vence en 2 días"
    Y las tareas deben marcarse con indicador visual de urgencia

  Escenario: Marcar tarea como completada y avanzar trámite
    Dado que el oficial "Juan Pérez" tiene asignada la tarea "Verificar documentación inicial"
    Y la tarea corresponde al trámite "TRM-2026-200"
    Cuando el oficial marca la tarea como "Completada"
    Y registra la observación "Documentación completa y verificada"
    Entonces el estado de la tarea debe cambiar a "Completada"
    Y se debe registrar la fecha y hora de finalización
    Y si todas las tareas de la etapa están completadas
    Entonces el trámite debe avanzar automáticamente a la siguiente etapa
    Y se debe crear las tareas correspondientes a la nueva etapa

#  Escenario: Reasignar tarea manualmente por especialización
#    Dado que el oficial "Juan Pérez" tiene asignada la tarea "Validar título médico"
#    Y la tarea requiere especialización en "Títulos Extranjeros"
#    Cuando un administrador reasigna la tarea al oficial "María García"
#    Y registra el motivo "Requiere especialización en títulos extranjeros"
#    Entonces la tarea debe reasignarse a "María García"
#    Y se debe notificar a ambos oficiales del cambio
#    Y la carga de trabajo debe actualizarse para ambos oficiales
#    Y el historial debe registrar la reasignación manual

#  LA PARTE DE ESPECIALIZACION ES ALGO QUE LO CONSIDERARIA OPCIONAL CON ESO SE PUEDE SIMPLIFICAR EL CODIGO