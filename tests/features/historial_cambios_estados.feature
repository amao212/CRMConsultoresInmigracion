# language: es
Característica: Historial de cambios de estados del trámite
  Como tramitador o solicitante
  Quiero consultar el historial de cambios de estado de un trámite
  Para tener trazabilidad completa de las acciones realizadas y conocer la evolución del expediente

  Antecedentes:
    Dado que existe un solicitante autenticado en el sistema
    Y que existe un tramitador activo asignado
    Y que se ha creado un nuevo trámite en estado "Pendiente"

  Escenario: Registro automático del estado inicial en el historial
    Dado que el trámite acaba de ser creado exitosamente
    Cuando se consulta el historial de cambios del trámite
    Entonces debe existir un registro inicial con el estado "Pendiente"
    Y el registro debe indicar la fecha y hora de creación

  Escenario: Registro de cambio de estado a Aprobado
    Dado que el trámite se encuentra en estado "Pendiente"
    Cuando el tramitador cambia el estado del trámite a "Aprobado"
    Entonces el sistema debe crear un nuevo registro en el historial
    Y el registro debe mostrar el estado anterior "Pendiente" y el nuevo estado "Aprobado"
    Y debe quedar registrado el tramitador que realizó la acción

  Escenario: Registro de cambio de estado a Rechazado con motivo
    Dado que el trámite se encuentra en estado "Pendiente"
    Cuando el tramitador cambia el estado del trámite a "Rechazado" con un motivo de justificación
    Entonces el sistema debe crear un nuevo registro en el historial con el estado "Rechazado"
    Y el registro debe incluir el motivo de rechazo proporcionado
    Y el historial debe mostrar los eventos ordenados cronológicamente
