# language:es
Característica: Gestión de Plantillas Maestras de Documentos
  Como solicitante de un trámite migratorio
  Quiero descargar las plantillas oficiales y subir los documentos completados
  Para asegurar que mi expediente cumpla con los requisitos de formato y contenido

  Antecedentes:
    Dado que existe un usuario solicitante autenticado en el sistema
    Y que existe una plantilla maestra activa configurada para el trámite "Visa de Turismo"
      | nombre_plantilla       | segmento | archivo_base      |
      | Formulario de Solicitud| Visas    | plantilla_base.pdf|

  Escenario: Descargar la plantilla maestra correspondiente al trámite
    Dado que el solicitante inicia un nuevo trámite de tipo "Visa de Turismo"
    Cuando el solicitante solicita descargar la plantilla asociada al trámite
    Entonces el sistema debe permitir descargar la plantilla asociada
    Y el archivo descargado debe ser un PDF

  Escenario: Subir el documento completado por primera vez (Generación v1)
    Dado que el solicitante tiene un trámite activo de tipo "Visa de Turismo"
    Cuando el solicitante sube un archivo PDF completado para este trámite
    Entonces el sistema debe guardar el documento exitosamente
    Y debe registrarse un documento asociado al trámite
    Y la versión registrada debe ser 1

  Escenario: Subir una corrección del documento (Control de versiones)
    Dado que el solicitante tiene un trámite activo de tipo "Visa de Turismo"
    Y que ya existe un documento cargado previamente para este trámite con versión 1
    Cuando el solicitante sube un nuevo archivo PDF corregido para el mismo trámite
    Entonces el sistema debe guardar el nuevo documento como una nueva versión
    Y la versión registrada debe incrementarse a 2

  Escenario: Subir los 2 documentos completados por primera vez
    Dado que el solicitante tiene un trámite activo de tipo "Visa de Turismo"
    Cuando el solicitante sube dos archivos PDF completados para este trámite
    Entonces el sistema debe guardar los documentos exitosamente
    Y debe registrarse dos documentos asociados al trámite