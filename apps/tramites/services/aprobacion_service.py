"""
Servicio para que los empleados aprueben o rechacen trámites asignados.
"""
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django.db import transaction
from apps.tramites.models import Tramite, HistorialCambios


class AprobacionTramiteService:
    """
    Servicio para gestionar la aprobación/rechazo de trámites por empleados.
    """

    @staticmethod
    def validar_empleado_asignado(tramite: Tramite, empleado) -> bool:
        """
        Valida que el empleado sea el asignado al trámite.

        Args:
            tramite: Trámite a validar
            empleado: Usuario empleado que intenta aprobar/rechazar

        Returns:
            True si es válido

        Raises:
            PermissionDenied: Si el empleado no es el asignado
        """
        # Validar que el usuario sea empleado
        if empleado.rol != 'EMPLEADO':
            raise PermissionDenied(f"El usuario {empleado.email} no es un empleado.")

        # Validar que el trámite tenga empleado asignado
        if not tramite.empleado_asignado:
            raise PermissionDenied(f"El trámite #{tramite.id} no tiene empleado asignado.")

        # Validar que sea el empleado asignado
        if tramite.empleado_asignado.id != empleado.id:
            raise PermissionDenied(
                f"El empleado {empleado.email} no está asignado al trámite #{tramite.id}. "
                f"Asignado: {tramite.empleado_asignado.email}"
            )

        return True

    @staticmethod
    @transaction.atomic
    def aprobar_tramite(tramite_id: int, empleado) -> Tramite:
        """
        Aprueba un trámite asignado al empleado.

        Args:
            tramite_id: ID del trámite a aprobar
            empleado: Usuario empleado que aprueba

        Returns:
            Tramite aprobado

        Raises:
            PermissionDenied: Si el empleado no es el asignado
            ValidationError: Si el trámite no se puede aprobar
        """
        try:
            tramite = Tramite.objects.select_related('empleado_asignado', 'solicitante').get(id=tramite_id)
        except Tramite.DoesNotExist:
            raise ValidationError(f"El trámite #{tramite_id} no existe.")

        # Validar que el empleado esté asignado
        AprobacionTramiteService.validar_empleado_asignado(tramite, empleado)

        # Validar que el trámite esté en estado PENDIENTE
        if tramite.estado != 'PENDIENTE':
            raise ValidationError(
                f"El trámite #{tramite_id} no está en estado PENDIENTE (estado actual: {tramite.estado}). "
                "Solo se pueden aprobar trámites pendientes."
            )

        estado_anterior = tramite.estado
        
        # Aprobar el trámite
        tramite.estado = 'APROBADO'
        tramite.fecha_aprobacion = timezone.now()
        tramite.motivo_rechazo = None  # Limpiar motivo de rechazo si existía
        tramite.save(update_fields=['estado', 'fecha_aprobacion', 'motivo_rechazo'])

        # Registrar historial
        HistorialCambios.objects.create(
            tramite=tramite,
            descripcion=f"Trámite aprobado por {empleado.nombre}",
            usuario=empleado,
            estado_anterior=estado_anterior,
            estado_nuevo='APROBADO'
        )

        print(f"✅ Trámite #{tramite.id} APROBADO por empleado {empleado.email}")
        print(f"   Solicitante: {tramite.solicitante.email}")
        print(f"   Fecha aprobación: {tramite.fecha_aprobacion}")

        return tramite

    @staticmethod
    @transaction.atomic
    def rechazar_tramite(tramite_id: int, empleado, motivo: str) -> Tramite:
        """
        Rechaza un trámite asignado al empleado.

        Args:
            tramite_id: ID del trámite a rechazar
            empleado: Usuario empleado que rechaza
            motivo: Motivo del rechazo

        Returns:
            Tramite rechazado

        Raises:
            PermissionDenied: Si el empleado no es el asignado
            ValidationError: Si el trámite no se puede rechazar o falta el motivo
        """
        if not motivo or not motivo.strip():
            raise ValidationError("Debe proporcionar un motivo para rechazar el trámite.")

        try:
            tramite = Tramite.objects.select_related('empleado_asignado', 'solicitante').get(id=tramite_id)
        except Tramite.DoesNotExist:
            raise ValidationError(f"El trámite #{tramite_id} no existe.")

        # Validar que el empleado esté asignado
        AprobacionTramiteService.validar_empleado_asignado(tramite, empleado)

        # Validar que el trámite esté en estado PENDIENTE
        if tramite.estado != 'PENDIENTE':
            raise ValidationError(
                f"El trámite #{tramite_id} no está en estado PENDIENTE (estado actual: {tramite.estado}). "
                "Solo se pueden rechazar trámites pendientes."
            )

        estado_anterior = tramite.estado

        # Rechazar el trámite
        tramite.estado = 'RECHAZADO'
        tramite.fecha_rechazo = timezone.now()
        tramite.motivo_rechazo = motivo.strip()
        tramite.fecha_aprobacion = None  # Limpiar fecha de aprobación si existía
        tramite.save(update_fields=['estado', 'fecha_rechazo', 'motivo_rechazo', 'fecha_aprobacion'])

        # Registrar historial
        HistorialCambios.objects.create(
            tramite=tramite,
            descripcion=f"Trámite rechazado por {empleado.nombre}. Motivo: {motivo.strip()}",
            usuario=empleado,
            estado_anterior=estado_anterior,
            estado_nuevo='RECHAZADO'
        )

        print(f"❌ Trámite #{tramite.id} RECHAZADO por empleado {empleado.email}")
        print(f"   Solicitante: {tramite.solicitante.email}")
        print(f"   Motivo: {motivo}")
        print(f"   Fecha rechazo: {tramite.fecha_rechazo}")

        return tramite

    @staticmethod
    def obtener_tramites_asignados(empleado):
        """
        Obtiene todos los trámites asignados a un empleado.

        Args:
            empleado: Usuario empleado

        Returns:
            QuerySet de trámites asignados
        """
        if empleado.rol != 'EMPLEADO':
            raise PermissionDenied(f"El usuario {empleado.email} no es un empleado.")

        tramites = Tramite.objects.filter(
            empleado_asignado=empleado
        ).select_related('solicitante').order_by('-fecha_inicio')

        return tramites

    @staticmethod
    def obtener_tramites_pendientes(empleado):
        """
        Obtiene los trámites pendientes asignados a un empleado.

        Args:
            empleado: Usuario empleado

        Returns:
            QuerySet de trámites pendientes
        """
        if empleado.rol != 'EMPLEADO':
            raise PermissionDenied(f"El usuario {empleado.email} no es un empleado.")

        tramites = Tramite.objects.filter(
            empleado_asignado=empleado,
            estado='PENDIENTE'
        ).select_related('solicitante').order_by('-fecha_inicio')

        return tramites
