# language:es
Característica: Control de versiones y registro de cambios en documentos
  Como solicitante o tramitador
  Quiero que el sistema gestione automáticamente las versiones de los documentos y registre cada cambio
  Para mantener la integridad del expediente y tener trazabilidad de las actualizaciones

  Antecedentes:
    Dado que existe un solicitante autenticado en el sistema
    Y que existe un trámite activo de tipo "Visa de Turismo"
    Y que existe una plantilla maestra activa para este tipo de trámite

  Escenario: Primera carga de documento genera versión inicial y registro
    Cuando el solicitante sube un documento PDF para el trámite
    Entonces el sistema debe registrar el documento con versión 1
    Y se debe crear un registro en el historial indicando "Carga inicial de documento"
    Y el registro debe asociar la acción al solicitante

  Escenario: Actualización de documento incrementa versión y registra cambio
    Dado que ya existe un documento cargado previamente con versión 1
    Cuando el solicitante sube una nueva versión del mismo documento
    Entonces el sistema debe registrar el nuevo documento con versión 2
    Y se debe crear un nuevo registro en el historial indicando "Actualización de documento"
    Y el historial debe mostrar ambos eventos ordenados cronológicamente

  Escenario: Consultar historial de versiones del documento
    Dado que existen múltiples versiones cargadas para un documento del trámite
    Cuando se consulta el historial de cambios del trámite
    Entonces se deben listar todas las versiones del documento
    Y cada entrada debe mostrar la fecha, el usuario y la versión correspondiente
