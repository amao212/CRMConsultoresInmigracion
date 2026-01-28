# language:es
Característica: Determinación de requisitos por modalidad migratoria
  Como oficial de migración o solicitante
  Quiero que el sistema determine automáticamente los requisitos y plazos según la modalidad del trámite
  Para asegurar que se presente la documentación correcta y conocer los tiempos estimados de respuesta

  Antecedentes:
    Dado que existe un solicitante autenticado en el sistema
    Y que existen configuraciones de requisitos para las modalidades "Turismo" y "Trabajo"

  Escenario: Determinación de requisitos para trámite de Turismo
    Cuando el solicitante inicia un trámite de modalidad "Turismo"
    Entonces el sistema debe listar los requisitos obligatorios para "Turismo"
    Y el plazo estimado de respuesta debe corresponder a la modalidad "Turismo"

  Escenario: Determinación de requisitos para trámite de Trabajo
    Cuando el solicitante inicia un trámite de modalidad "Trabajo"
    Entonces el sistema debe listar los requisitos obligatorios para "Trabajo"
    Y la lista de requisitos debe ser diferente a la de "Turismo"
    Y el plazo estimado de respuesta debe corresponder a la modalidad "Trabajo"

  Escenario: Actualización de requisitos al cambiar la modalidad
    Dado que el solicitante ha iniciado un trámite de modalidad "Turismo"
    Cuando el solicitante cambia la modalidad del trámite a "Trabajo" antes de enviarlo
    Entonces el sistema debe actualizar la lista de requisitos a los de "Trabajo"
    Y el plazo estimado debe actualizarse acorde a la nueva modalidad
