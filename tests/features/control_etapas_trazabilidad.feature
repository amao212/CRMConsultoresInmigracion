# language:es
Característica: Control de etapas y trazabilidad del expediente
  Como empleado
  quiero controlar las etapas del trámite y mantener trazabilidad completa
  para garantizar transparencia y seguimiento en tiempo real

  Antecedentes:
    Dado que existen los siguientes estados de trámite en el sistema
      | estado     | descripcion             |
      | PENDIENTE  | Pendiente de Aprobación |
      | APROBADO   | Aprobado                |
      | RECHAZADO  | Rechazado               |
      | EN_PROCESO | En Proceso              |
      | COMPLETADO | Completado              |
      | RETRASADO  | Retrasado               |

  Escenario: Iniciar un nuevo trámite
    Dado que un solicitante inicia un trámite de modalidad "Trabajo"
    Cuando se registra el trámite con código "TRM-2026-100"
    Entonces el trámite debe iniciar en el estado "PENDIENTE"
#    Y se debe generar un número de expediente único
#    Y se debe asignar automáticamente a un oficial disponible

#  Escenario: Avanzar automáticamente a siguiente etapa
#    Dado que el trámite "TRM-2026-100" está en la etapa "Recepción"
#    Y todos los documentos obligatorios están en estado "Aprobado"
#    Cuando el sistema verifica la completitud
#    Entonces el trámite debe avanzar automáticamente a la etapa "Documentos Completos"
#    Y se debe registrar la fecha y hora del cambio
#    Y se debe registrar el motivo "Documentos completos y aprobados"


#  Escenario: Avanzar manualmente a siguiente etapa
#    Dado que el trámite "TRM-2026-100" está en la etapa "Documentos Completos"
#    Cuando el oficial "Juan Pérez" avanza el trámite a la etapa "Evaluación"
#    Y registra la observación "Expediente completo, procede evaluación"
#    Entonces la etapa debe cambiar a "Evaluación"
#    Y se debe registrar el oficial responsable del cambio
#    Y se debe registrar la fecha y hora del cambio
#    Y el historial debe reflejar el cambio de etapa

#  Escenario: Retroceder trámite a etapa anterior por documentos faltantes
#    Dado que el trámite "TRM-2026-100" está en la etapa "Evaluación"
#    Cuando el oficial detecta que falta el documento "Certificado médico"
#    Y el oficial retrocede el trámite a la etapa "Recepción"
#    Y registra el motivo "Falta certificado médico actualizado"
#    Entonces la etapa debe cambiar a "Recepción"
#    Y el estado debe cambiar a "Documentos Pendientes"
#    Y se debe notificar al solicitante con los documentos faltantes
#    Y el historial debe registrar el retroceso con el motivo

  Escenario: Consultar historial completo de cambios de estado
    Dado que el trámite "TRM-2026-100" tiene el siguiente historial
      | fecha      | hora  | estado_anterior | estado_nuevo | oficial      | descripcion                         |
      | 2026-01-10 | 09:00 | PENDIENTE       | EN_PROCESO   | Juan Pérez   | Inicio de revisión                  |
      | 2026-01-15 | 14:30 | EN_PROCESO      | APROBADO     | Juan Pérez   | Documentos completos y aprobados    |
    Cuando el solicitante consulta el historial del trámite
    Entonces se debe mostrar el historial completo ordenado cronológicamente
#    Y cada entrada debe incluir fecha, hora, etapa, estado, oficial y motivo


#  Escenario: Monitorear trámite en tiempo real
#    Dado que el trámite "TRM-2026-100" está en la etapa "Evaluación"
#    Y el estado es "Activo"
#    Cuando el solicitante consulta el estado del trámite
#    Entonces se debe mostrar la etapa actual "Evaluación"
#    Y se debe mostrar el progreso "4 de 7 etapas completadas"

  Escenario: Finalizar trámite exitosamente (Aprobación)
    Dado que el trámite "TRM-2026-100" está en estado "PENDIENTE"
    Cuando el oficial aprueba el trámite
    Entonces el estado debe cambiar a "APROBADO"
    Y se debe registrar la fecha de aprobación

  Escenario: Rechazar trámite
    Dado que el trámite "TRM-2026-101" está en estado "PENDIENTE"
    Cuando el oficial rechaza el trámite
    Y registra el motivo "Documentación fraudulenta detectada"
    Entonces el estado debe cambiar a "RECHAZADO"
    Y se debe registrar la fecha de rechazo
    Y se debe registrar el motivo del rechazo

#  Escenario: Calcular métricas de tiempo por etapa
#    Dado que existen múltiples trámites finalizados en el último mes
#    Cuando se solicita el reporte de tiempos promedio por etapa
#    Entonces se debe calcular el tiempo promedio en cada etapa
#    Y se debe identificar las etapas con mayor duración
#    Y se debe generar un reporte con las siguientes métricas
#      | etapa                | tiempo_promedio_dias | cantidad_tramites |
#      | Recepción            | 3.5                  | 150               |
#      | Documentos Completos | 2.0                  | 150               |
#      | Evaluación           | 8.0                  | 150               |
#      | Entrevista           | 5.0                  | 120               |
#      | Aprobación           | 2.5                  | 100               |
#      | Emisión de Visa      | 3.0                  | 100               |