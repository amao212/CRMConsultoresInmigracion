from apps.usuarios.models import UsuarioCRM as Usuario
from apps.tramites.models import Tarea, Notificacion, Cita

TAREAS_POR_TRAMITE = {
    "Residencia Permanente": ["Revisar formulario I-485", "Agendar entrevista", "Preparar documentos de soporte"],
    "Visa de Trabajo": ["Verificar oferta de empleo", "Presentar formulario I-129", "Coordinar con el empleador"],
}

def asignar_tareas_automaticamente(tramite):
    empleado_disponible = Usuario.objects.filter(rol='EMPLEADO').first() # Simulación simple
    if not empleado_disponible:
        return

    tareas_a_crear = TAREAS_POR_TRAMITE.get(tramite.nombre, [])
    for nombre_tarea in tareas_a_crear:
        Tarea.objects.create(
            tramite=tramite,
            nombre=nombre_tarea,
            asignado_a=empleado_disponible
        )

    # Notificar al empleado
    Notificacion.objects.create(
        destinatario=empleado_disponible,
        mensaje=f"Se te han asignado nuevas tareas para el trámite '{tramite.nombre}'."
    )
    # Notificar vencimiento (simulado)
    Notificacion.objects.create(
        destinatario=tramite.solicitante,
        mensaje=f"Recuerda que la fecha límite para tu trámite '{tramite.nombre}' es el {tramite.fecha_limite.strftime('%d/%m/%Y')}."
    )

def reprogramar_cita(cita):
    cita.cancelada = True
    cita.save()

    # Lógica para liberar el horario en la agenda (simulado)
    print(f"Horario de {cita.fecha_hora} liberado para el empleado {cita.empleado.email}")

    # Notificar al empleado
    Notificacion.objects.create(
        destinatario=cita.empleado,
        mensaje=f"La cita para el trámite '{cita.tramite.nombre}' del {cita.fecha_hora.strftime('%d/%m/%Y a las %H:%M')} ha sido cancelada."
    )
