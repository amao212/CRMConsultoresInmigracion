"""
Servicio para asignar tramitadores a trámites de manera automática.
Usa algoritmo round-robin para distribuir equitativamente la carga de trabajo.
"""
from django.db.models import Count, Q
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.tramites.models import Tramite, UltimaAsignacion

# Obtener el modelo de usuario configurado
Usuario = get_user_model()


class AsignacionTramitadorService:
    """
    Servicio para asignar tramitadores a trámites automáticamente.
    """

    @staticmethod
    def obtener_tramitador_disponible():
        """
        Obtiene el siguiente tramitador disponible usando un algoritmo Round-Robin (circular).
        Garantiza una distribución equitativa y consistente.
        
        El ciclo es: Tramitador1 -> Tramitador2 -> ... -> TramitadorN -> Tramitador1

        Returns:
            Usuario (tramitador) seleccionado, o None si no hay tramitadores
        """
        try:
            with transaction.atomic():
                # Obtener o crear el registro de última asignación y bloquearlo para evitar condiciones de carrera
                # Usamos id=1 ya que solo necesitamos un registro global
                registro_asignacion, created = UltimaAsignacion.objects.select_for_update().get_or_create(id=1)
                
                ultimo_id = registro_asignacion.ultimo_tramitador_id

                # Obtener todos los tramitadores activos ordenados por ID para garantizar orden consistente
                tramitadores = Usuario.objects.filter(
                    rol='TRAMITADOR',
                    is_active=True
                ).order_by('id')

                if not tramitadores.exists():
                    print("⚠️ No hay tramitadores disponibles para asignar")
                    return None

                tramitador_seleccionado = None

                if ultimo_id:
                    # Buscar el siguiente tramitador con ID mayor al último asignado
                    # Esto encuentra al "siguiente" en la lista ordenada
                    tramitador_seleccionado = tramitadores.filter(id__gt=ultimo_id).first()

                # Si no hay siguiente (llegamos al final de la lista) o no había último ID (primera vez),
                # volvemos al principio del ciclo (Round-Robin)
                if not tramitador_seleccionado:
                    tramitador_seleccionado = tramitadores.first()

                # Actualizar el registro de última asignación
                if tramitador_seleccionado:
                    registro_asignacion.ultimo_tramitador_id = tramitador_seleccionado.id
                    registro_asignacion.save()
                    print(f"✅ Tramitador asignado (Round-Robin): {tramitador_seleccionado.email} (ID: {tramitador_seleccionado.id})")
                    return tramitador_seleccionado
                
                return None
        except Exception as e:
            print(f"❌ Error en algoritmo de asignación: {e}")
            # Fallback: intentar obtener el primero disponible sin bloqueo si falla la transacción
            return Usuario.objects.filter(rol='TRAMITADOR', is_active=True).first()

    @staticmethod
    def asignar_tramitador_a_tramite(tramite: Tramite) -> bool:
        """
        Asigna un tramitador disponible a un trámite de forma automática.

        Args:
            tramite: Trámite al que se le asignará un tramitador

        Returns:
            True si se asignó exitosamente, False si no hay tramitadores disponibles
        """
        if tramite.tramitador_asignado:
            print(f"⚠️ El trámite #{tramite.id} ya tiene tramitador asignado: {tramite.tramitador_asignado.email}")
            return True

        tramitador = AsignacionTramitadorService.obtener_tramitador_disponible()

        if tramitador:
            tramite.tramitador_asignado = tramitador
            tramite.save(update_fields=['tramitador_asignado'])
            print(f"✅ Trámite #{tramite.id} asignado a tramitador {tramitador.email}")
            return True
        else:
            print(f"❌ No se pudo asignar tramitador al trámite #{tramite.id}")
            return False

    @staticmethod
    def reasignar_tramitador_a_tramite(tramite: Tramite, nuevo_tramitador: Usuario) -> bool:
        """
        Reasigna un trámite a un tramitador específico.
        Solo puede ser usado por administradores.

        Args:
            tramite: Trámite a reasignar
            nuevo_tramitador: Nuevo tramitador a asignar

        Returns:
            True si se reasignó exitosamente
        """
        if nuevo_tramitador.rol != 'TRAMITADOR':
            raise ValueError(f"El usuario {nuevo_tramitador.email} no es un tramitador")

        tramitador_anterior = tramite.tramitador_asignado
        tramite.tramitador_asignado = nuevo_tramitador
        tramite.save(update_fields=['tramitador_asignado'])

        print(f"✅ Trámite #{tramite.id} reasignado de {tramitador_anterior} a {nuevo_tramitador.email}")
        return True

    @staticmethod
    def obtener_estadisticas_tramitadores():
        """
        Obtiene estadísticas de carga de trabajo de todos los tramitadores.

        Returns:
            QuerySet con estadísticas de cada tramitador
        """
        tramitadores_stats = Usuario.objects.filter(
            rol='TRAMITADOR',
            is_active=True
        ).annotate(
            total_tramites=Count('tramites_asignados'),
            tramites_pendientes=Count(
                'tramites_asignados',
                filter=Q(tramites_asignados__estado='PENDIENTE')
            ),
            tramites_aprobados=Count(
                'tramites_asignados',
                filter=Q(tramites_asignados__estado='APROBADO')
            ),
            tramites_rechazados=Count(
                'tramites_asignados',
                filter=Q(tramites_asignados__estado='RECHAZADO')
            ),
            tramites_en_proceso=Count(
                'tramites_asignados',
                filter=Q(tramites_asignados__estado='EN_PROCESO')
            ),
            tramites_completados=Count(
                'tramites_asignados',
                filter=Q(tramites_asignados__estado='COMPLETADO')
            )
        ).order_by('-total_tramites')

        return tramitadores_stats
