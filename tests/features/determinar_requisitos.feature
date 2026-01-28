# language:es
Característica: Determinación de requisitos por modalidad migratoria
  Como oficial de migración
  quiero determinar automáticamente los requisitos necesarios según la modalidad migratoria
  para agilizar el proceso de evaluación de solicitudes

  Antecedentes:
    Dado que existen plantillas de documentos configuradas para las siguientes modalidades
      | modalidad               | segmento   |
      | Turismo                 | Visas      |
      | Trabajo                 | Visas      |
      | Estudio                 | Visas      |
      | Residencia Permanente   | Residencia |

  Escenario: Determinar requisitos para trámite de turismo
    Dado que un solicitante inicia un trámite de modalidad "Turismo"
    Cuando el sistema determina los requisitos basados en la plantilla
    Entonces se deben solicitar los siguientes campos en el formulario
      | campo                            | tipo     |
      | Nombre Completo                  | text     |
      | Número de Identificación/Pasaporte| text     |
      | Propósito del Viaje              | textarea |
    Y el plazo de procesamiento estimado es de 90 días

  Escenario: Determinar requisitos para trámite de trabajo
    Dado que un solicitante inicia un trámite de modalidad "Trabajo"
    Cuando el sistema determina los requisitos basados en la plantilla
    Entonces se deben solicitar los siguientes campos en el formulario
      | campo                            | tipo     |
      | Empresa Empleadora               | text     |
      | Cargo a Desempeñar               | text     |
    Y el plazo de procesamiento estimado es de 90 días

#  Escenario: Actualizar requisitos cuando cambia la modalidad (Funcionalidad futura)
#    Dado que existe un trámite iniciado con modalidad "Turismo"
#    Y el trámite tiene el estado "En Revisión"
#    Cuando el solicitante cambia la modalidad a "Trabajo"
#    Entonces el sistema debe actualizar la lista de requisitos
#    Y se debe notificar al solicitante de los nuevos documentos requeridos
#    Y el estado del trámite debe cambiar a "Documentos Pendientes"