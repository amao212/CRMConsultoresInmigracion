from apps.tramites.models import Tramite, Alerta, HistorialCambios
from apps.usuarios.models import UsuarioCRM as Usuario
from django.utils import timezone

def detectar_retrasos():
    tramites_retrasados = Tramite.objects.filter(fecha_limite__lt=timezone.now(), estado='EN_PROCESO')
    administradores = Usuario.objects.filter(rol='ADMINISTRADOR')

    for tramite in tramites_retrasados:
        tramite.estado = 'RETRASADO'
        tramite.save()

        # Crear historial de cambios
        HistorialCambios.objects.create(
            tramite=tramite,
            descripcion=f"El trámite '{tramite.nombre}' ha sido marcado como retrasado."
        )

        # Enviar alerta a todos los administradores
        for admin in administradores:
            Alerta.objects.create(
                administrador=admin,
                mensaje=f"Alerta: El trámite '{tramite.nombre}' del solicitante '{tramite.solicitante.email}' ha superado el tiempo límite."
            )
