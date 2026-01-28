# language: es
Característica: Asignación automática de estados del trámite
  Como tramitador encargado de la gestión migratoria
  Quiero que el sistema actualice automáticamente el estado de los trámites al realizar acciones clave
  Para garantizar la consistencia del flujo de trabajo y evitar errores humanos en la actualización de estados

  Antecedentes:
    Dado que existe la configuración necesaria para los flujos de trámites en el sistema

  Escenario: Asignación del estado inicial al crear una solicitud
    Dado que un solicitante completa el registro de una nueva solicitud de trámite
    Cuando el sistema confirma la creación del expediente
    Entonces el trámite debe quedar automáticamente en estado "Pendiente"
    Y no debe requerir intervención manual para establecer este estado inicial

  Escenario: Transición automática a Aprobado tras la validación positiva
    Dado que existe un trámite en estado "Pendiente" asignado a un tramitador
    Cuando el tramitador ejecuta la acción de aprobación del trámite
    Entonces el sistema debe cambiar automáticamente el estado del trámite a "Aprobado"
    Y se debe registrar la fecha de aprobación en el sistema

  Escenario: Transición automática a Rechazado tras una evaluación negativa
    Dado que existe un trámite en estado "Pendiente" asignado a un tramitador
    Cuando el tramitador ejecuta la acción de rechazo ingresando un motivo de justificación
    Entonces el sistema debe cambiar automáticamente el estado del trámite a "Rechazado"
    Y el motivo del rechazo debe quedar asociado al expediente
