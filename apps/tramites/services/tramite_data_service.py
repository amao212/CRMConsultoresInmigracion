"""
Servicio para manejar la persistencia segura de datos dinámicos de trámites.
Garantiza que solo el solicitante propietario pueda modificar sus datos.
"""
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from apps.tramites.models import Tramite, PlantillaDocumento, CampoPlantilla


class TramiteDataService:
    """
    Servicio para gestionar los datos dinámicos de trámites con validaciones de seguridad.
    """

    @staticmethod
    def validar_propiedad_tramite(tramite: Tramite, usuario):
        """
        Valida que el usuario sea el propietario del trámite.
        Lanza PermissionDenied si no es el propietario.
        """
        if tramite.solicitante.id != usuario.id:
            raise PermissionDenied(
                f"El usuario {usuario.email} no tiene permiso para modificar el trámite #{tramite.id}"
            )
        return True

    @staticmethod
    def validar_datos_formulario(form_data: dict, plantilla: PlantillaDocumento) -> dict:
        """
        Valida que los datos del formulario correspondan a los campos definidos en la plantilla.
        Retorna un diccionario limpio con solo los campos válidos.
        """
        campos_validos = plantilla.campos.all()
        datos_limpios = {}
        errores = []

        for campo in campos_validos:
            nombre_tecnico = campo.nombre_tecnico
            valor = form_data.get(nombre_tecnico)

            # Validar campos requeridos
            if campo.es_requerido and not valor:
                errores.append(f"El campo '{campo.nombre_campo}' es requerido.")
                continue

            # Agregar solo si existe el valor
            if valor:
                datos_limpios[nombre_tecnico] = str(valor).strip()

        if errores:
            raise ValidationError(errores)

        return datos_limpios

    @staticmethod
    @transaction.atomic
    def guardar_datos_formulario(tramite_id: int, usuario, form_data: dict) -> Tramite:
        """
        Guarda los datos del formulario en el trámite de forma segura.

        Validaciones:
        1. El trámite existe
        2. El usuario es el propietario del trámite
        3. Los datos son válidos según la plantilla

        Args:
            tramite_id: ID del trámite a actualizar
            usuario: Usuario que intenta modificar (debe ser el solicitante)
            form_data: Diccionario con los datos del formulario

        Returns:
            Tramite actualizado

        Raises:
            PermissionDenied: Si el usuario no es el propietario
            ValidationError: Si los datos no son válidos
        """
        try:
            # 1. Obtener el trámite y validar que existe
            tramite = Tramite.objects.select_related('solicitante').get(id=tramite_id)
        except Tramite.DoesNotExist:
            raise ValidationError(f"El trámite #{tramite_id} no existe.")

        # 2. Validar propiedad del trámite
        TramiteDataService.validar_propiedad_tramite(tramite, usuario)

        # 3. Obtener la plantilla asociada (a través del nombre del trámite)
        try:
            plantilla = PlantillaDocumento.objects.get(tipo_especifico=tramite.nombre, activo=True)
        except PlantillaDocumento.DoesNotExist:
            raise ValidationError(f"No se encontró plantilla activa para el trámite '{tramite.nombre}'")

        # 4. Validar y limpiar datos
        datos_limpios = TramiteDataService.validar_datos_formulario(form_data, plantilla)

        # 5. Guardar datos en el campo JSON
        tramite.datos_formulario = datos_limpios
        tramite.save(update_fields=['datos_formulario'])

        return tramite

    @staticmethod
    def obtener_datos_tramite(tramite_id: int, usuario) -> dict:
        """
        Obtiene los datos del formulario de un trámite de forma segura.

        Args:
            tramite_id: ID del trámite
            usuario: Usuario que solicita los datos

        Returns:
            Diccionario con los datos del formulario

        Raises:
            PermissionDenied: Si el usuario no es el propietario
        """
        try:
            tramite = Tramite.objects.select_related('solicitante').get(id=tramite_id)
        except Tramite.DoesNotExist:
            raise ValidationError(f"El trámite #{tramite_id} no existe.")

        # Validar propiedad
        TramiteDataService.validar_propiedad_tramite(tramite, usuario)

        return tramite.datos_formulario or {}

    @staticmethod
    def obtener_tramite_con_datos(tramite_id: int, solicitante_id: int) -> Tramite:
        """
        Obtiene un trámite filtrando por ID de trámite y ID de solicitante.
        Método seguro para obtener datos antes de generar PDF.

        Args:
            tramite_id: ID del trámite
            solicitante_id: ID del solicitante (para validación adicional)

        Returns:
            Tramite con sus datos

        Raises:
            ValidationError: Si el trámite no existe o no pertenece al solicitante
        """
        try:
            tramite = Tramite.objects.select_related('solicitante').get(
                id=tramite_id,
                solicitante_id=solicitante_id
            )
            return tramite
        except Tramite.DoesNotExist:
            raise ValidationError(
                f"El trámite #{tramite_id} no existe o no pertenece al solicitante #{solicitante_id}"
            )
