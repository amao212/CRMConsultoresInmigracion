"""
Servicio para asignar empleados a trámites de manera automática.
Usa algoritmo round-robin para distribuir equitativamente la carga de trabajo.
"""
from django.db.models import Count, Q
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.tramites.models import Tramite, UltimaAsignacion

# Obtener el modelo de usuario configurado
Usuario = get_user_model()


class AsignacionEmpleadoService:
    """
    Servicio para asignar empleados a trámites automáticamente.
    """

    @staticmethod
    def obtener_empleado_disponible():
        """
        Obtiene el siguiente empleado disponible usando un algoritmo Round-Robin (circular).
        Garantiza una distribución equitativa y consistente.
        
        El ciclo es: Empleado1 -> Empleado2 -> ... -> EmpleadoN -> Empleado1

        Returns:
            Usuario (empleado) seleccionado, o None si no hay empleados
        """
        try:
            with transaction.atomic():
                # Obtener o crear el registro de última asignación y bloquearlo para evitar condiciones de carrera
                # Usamos id=1 ya que solo necesitamos un registro global
                registro_asignacion, created = UltimaAsignacion.objects.select_for_update().get_or_create(id=1)
                
                ultimo_id = registro_asignacion.ultimo_empleado_id

                # Obtener todos los empleados activos ordenados por ID para garantizar orden consistente
                empleados = Usuario.objects.filter(
                    rol='EMPLEADO',
                    is_active=True
                ).order_by('id')

                if not empleados.exists():
                    print("⚠️ No hay empleados disponibles para asignar")
                    return None

                empleado_seleccionado = None

                if ultimo_id:
                    # Buscar el siguiente empleado con ID mayor al último asignado
                    # Esto encuentra al "siguiente" en la lista ordenada
                    empleado_seleccionado = empleados.filter(id__gt=ultimo_id).first()

                # Si no hay siguiente (llegamos al final de la lista) o no había último ID (primera vez),
                # volvemos al principio del ciclo (Round-Robin)
                if not empleado_seleccionado:
                    empleado_seleccionado = empleados.first()

                # Actualizar el registro de última asignación
                if empleado_seleccionado:
                    registro_asignacion.ultimo_empleado_id = empleado_seleccionado.id
                    registro_asignacion.save()
                    print(f"✅ Empleado asignado (Round-Robin): {empleado_seleccionado.email} (ID: {empleado_seleccionado.id})")
                    return empleado_seleccionado
                
                return None
        except Exception as e:
            print(f"❌ Error en algoritmo de asignación: {e}")
            # Fallback: intentar obtener el primero disponible sin bloqueo si falla la transacción
            return Usuario.objects.filter(rol='EMPLEADO', is_active=True).first()

    @staticmethod
    def asignar_empleado_a_tramite(tramite: Tramite) -> bool:
        """
        Asigna un empleado disponible a un trámite de forma automática.

        Args:
            tramite: Trámite al que se le asignará un empleado

        Returns:
            True si se asignó exitosamente, False si no hay empleados disponibles
        """
        if tramite.empleado_asignado:
            print(f"⚠️ El trámite #{tramite.id} ya tiene empleado asignado: {tramite.empleado_asignado.email}")
            return True

        empleado = AsignacionEmpleadoService.obtener_empleado_disponible()

        if empleado:
            tramite.empleado_asignado = empleado
            tramite.save(update_fields=['empleado_asignado'])
            print(f"✅ Trámite #{tramite.id} asignado a empleado {empleado.email}")
            return True
        else:
            print(f"❌ No se pudo asignar empleado al trámite #{tramite.id}")
            return False

    @staticmethod
    def reasignar_empleado_a_tramite(tramite: Tramite, nuevo_empleado: Usuario) -> bool:
        """
        Reasigna un trámite a un empleado específico.
        Solo puede ser usado por administradores.

        Args:
            tramite: Trámite a reasignar
            nuevo_empleado: Nuevo empleado a asignar

        Returns:
            True si se reasignó exitosamente
        """
        if nuevo_empleado.rol != 'EMPLEADO':
            raise ValueError(f"El usuario {nuevo_empleado.email} no es un empleado")

        empleado_anterior = tramite.empleado_asignado
        tramite.empleado_asignado = nuevo_empleado
        tramite.save(update_fields=['empleado_asignado'])

        print(f"✅ Trámite #{tramite.id} reasignado de {empleado_anterior} a {nuevo_empleado.email}")
        return True

    @staticmethod
    def obtener_estadisticas_empleados():
        """
        Obtiene estadísticas de carga de trabajo de todos los empleados.

        Returns:
            QuerySet con estadísticas de cada empleado
        """
        empleados_stats = Usuario.objects.filter(
            rol='EMPLEADO',
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

        return empleados_stats
