"""
Servicio para que los tramitadores aprueben o rechacen trámites asignados.
"""
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django.db import transaction
from apps.tramites.models import Tramite, HistorialCambios


class AprobacionTramiteService:
    """
    Servicio para gestionar la aprobación/rechazo de trámites por tramitadores.
    """

    @staticmethod
    def validar_tramitador_asignado(tramite: Tramite, tramitador) -> bool:
        """
        Valida que el tramitador sea el asignado al trámite.

        Args:
            tramite: Trámite a validar
            tramitador: Usuario tramitador que intenta aprobar/rechazar

        Returns:
            True si es válido

        Raises:
            PermissionDenied: Si el tramitador no es el asignado
        """
        # Validar que el usuario sea tramitador
        if tramitador.rol != 'TRAMITADOR':
            raise PermissionDenied(f"El usuario {tramitador.email} no es un tramitador.")

        # Validar que el trámite tenga tramitador asignado
        if not tramite.tramitador_asignado:
            raise PermissionDenied(f"El trámite #{tramite.id} no tiene tramitador asignado.")

        # Validar que sea el tramitador asignado
        if tramite.tramitador_asignado.id != tramitador.id:
            raise PermissionDenied(
                f"El tramitador {tramitador.email} no está asignado al trámite #{tramite.id}. "
                f"Asignado: {tramite.tramitador_asignado.email}"
            )

        return True

    @staticmethod
    @transaction.atomic
    def aprobar_tramite(tramite_id: int, tramitador) -> Tramite:
        """
        Aprueba un trámite asignado al tramitador.

        Args:
            tramite_id: ID del trámite a aprobar
            tramitador: Usuario tramitador que aprueba

        Returns:
            Tramite aprobado

        Raises:
            PermissionDenied: Si el tramitador no es el asignado
            ValidationError: Si el trámite no se puede aprobar
        """
        try:
            tramite = Tramite.objects.select_related('tramitador_asignado', 'solicitante').get(id=tramite_id)
        except Tramite.DoesNotExist:
            raise ValidationError(f"El trámite #{tramite_id} no existe.")

        # Validar que el tramitador esté asignado
        AprobacionTramiteService.validar_tramitador_asignado(tramite, tramitador)

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
            descripcion=f"Trámite aprobado por {tramitador.nombre}",
            usuario=tramitador,
            estado_anterior=estado_anterior,
            estado_nuevo='APROBADO'
        )

        print(f"✅ Trámite #{tramite.id} APROBADO por tramitador {tramitador.email}")
        print(f"   Solicitante: {tramite.solicitante.email}")
        print(f"   Fecha aprobación: {tramite.fecha_aprobacion}")

        return tramite

    @staticmethod
    @transaction.atomic
    def rechazar_tramite(tramite_id: int, tramitador, motivo: str) -> Tramite:
        """
        Rechaza un trámite asignado al tramitador.

        Args:
            tramite_id: ID del trámite a rechazar
            tramitador: Usuario tramitador que rechaza
            motivo: Motivo del rechazo

        Returns:
            Tramite rechazado

        Raises:
            PermissionDenied: Si el tramitador no es el asignado
            ValidationError: Si el trámite no se puede rechazar o falta el motivo
        """
        if not motivo or not motivo.strip():
            raise ValidationError("Debe proporcionar un motivo para rechazar el trámite.")

        try:
            tramite = Tramite.objects.select_related('tramitador_asignado', 'solicitante').get(id=tramite_id)
        except Tramite.DoesNotExist:
            raise ValidationError(f"El trámite #{tramite_id} no existe.")

        # Validar que el tramitador esté asignado
        AprobacionTramiteService.validar_tramitador_asignado(tramite, tramitador)

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
            descripcion=f"Trámite rechazado por {tramitador.nombre}. Motivo: {motivo.strip()}",
            usuario=tramitador,
            estado_anterior=estado_anterior,
            estado_nuevo='RECHAZADO'
        )

        print(f"❌ Trámite #{tramite.id} RECHAZADO por tramitador {tramitador.email}")
        print(f"   Solicitante: {tramite.solicitante.email}")
        print(f"   Motivo: {motivo}")
        print(f"   Fecha rechazo: {tramite.fecha_rechazo}")

        return tramite

    @staticmethod
    def obtener_tramites_asignados(tramitador):
        """
        Obtiene todos los trámites asignados a un tramitador.

        Args:
            tramitador: Usuario tramitador

        Returns:
            QuerySet de trámites asignados
        """
        if tramitador.rol != 'TRAMITADOR':
            raise PermissionDenied(f"El usuario {tramitador.email} no es un tramitador.")

        tramites = Tramite.objects.filter(
            tramitador_asignado=tramitador
        ).select_related('solicitante').order_by('-fecha_inicio')

        return tramites

    @staticmethod
    def obtener_tramites_pendientes(tramitador):
        """
        Obtiene los trámites pendientes asignados a un tramitador.

        Args:
            tramitador: Usuario tramitador

        Returns:
            QuerySet de trámites pendientes
        """
        if tramitador.rol != 'TRAMITADOR':
            raise PermissionDenied(f"El usuario {tramitador.email} no es un tramitador.")

        tramites = Tramite.objects.filter(
            tramitador_asignado=tramitador,
            estado='PENDIENTE'
        ).select_related('solicitante').order_by('-fecha_inicio')

        return tramites
