# language:es
Característica: Asignación automática de tareas y tramitadores
  Como administrador del sistema
  Quiero que los trámites se asignen automáticamente a los tramitadores y se generen las tareas iniciales
  Para optimizar la distribución de la carga de trabajo y asegurar que ningún trámite quede sin atención

  Antecedentes:
    Dado que existen tramitadores activos disponibles en el sistema
    Y que existe un solicitante autenticado

  Escenario: Asignación automática de tramitador y tarea inicial al crear trámite
    Cuando el solicitante crea un nuevo trámite de tipo "Visa de Turismo"
    Entonces el sistema debe asignar automáticamente un tramitador al trámite
    Y se debe crear una tarea inicial "Revisar documentación" asociada al trámite
    Y la tarea debe estar en estado "Pendiente"

  Escenario: Distribución equitativa de trámites (Round-Robin)
    Dado que se ha asignado un trámite reciente al tramitador "A"
    Cuando se crea un segundo trámite nuevo en el sistema
    Entonces el sistema debe asignar este segundo trámite al tramitador "B"
    Y no debe asignarlo nuevamente al tramitador "A" para garantizar el balanceo
