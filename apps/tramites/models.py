import os
from django.apps import apps
from django.db import models
from django.conf import settings
from .storage import OverwriteStorage

def documento_upload_to(instance, filename):
    tramite = instance.tramite
    solicitante_id = tramite.solicitante.id
    nombre_documento = instance.nombre
    version = instance.version
    
    # Normalizar nombre del documento para el archivo (slug)
    documento_nombre_clean = nombre_documento.lower().replace(' ', '_')
    
    # Obtener extensión
    _, ext = os.path.splitext(filename)
    
    # Construir nombre: nombre_vX.ext
    new_filename = f"{documento_nombre_clean}_v{version}{ext}"
    
    # Segmento
    segmento = 'general'
    
    # Intentar obtener la plantilla
    PlantillaDocumento = apps.get_model('tramites', 'PlantillaDocumento')
    
    # Try to find template attached to tramite or by name
    plantilla = getattr(tramite, 'plantilla', None)
    if not plantilla:
        # Try to find by name
        plantilla = PlantillaDocumento.objects.filter(tipo_especifico=tramite.nombre).first()
            
    if plantilla:
        segmento = plantilla.segmento.lower().replace(' ', '_')
    elif hasattr(tramite, 'nombre'):
         segmento = tramite.nombre.split()[0].lower()

    return f"solicitante/solicitante_{solicitante_id:04d}/{segmento}/{new_filename}"

class Tramite(models.Model):
    ESTADOS = (('PENDIENTE', 'Pendiente de Aprobación'), ('APROBADO', 'Aprobado'), ('RECHAZADO', 'Rechazado'), ('EN_PROCESO', 'En Proceso'), ('COMPLETADO', 'Completado'), ('RETRASADO', 'Retrasado'))
    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tramites')
    empleado_asignado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='tramites_asignados', limit_choices_to={'rol': 'EMPLEADO'}, help_text="Empleado asignado automáticamente para revisar el trámite")
    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateTimeField()
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, help_text="Fecha en que el empleado aprobó el trámite")
    fecha_rechazo = models.DateTimeField(null=True, blank=True, help_text="Fecha en que el empleado rechazó el trámite")
    motivo_rechazo = models.TextField(blank=True, null=True, help_text="Razón del rechazo del trámite")
    datos_formulario = models.JSONField(default=dict, blank=True, help_text="Datos dinámicos del formulario del trámite")
    def __str__(self): return self.nombre
    class Meta:
        db_table = 'tramites_tramite'
        permissions = [("can_modify_own_tramite", "Puede modificar sus propios trámites"), ("can_approve_tramite", "Puede aprobar trámites")]

class Tarea(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='tareas')
    nombre = models.CharField(max_length=100)
    completada = models.BooleanField(default=False)
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_asignadas')
    def __str__(self): return self.nombre

class Documento(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='documentos')
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(upload_to=documento_upload_to, storage=OverwriteStorage())
    version = models.PositiveIntegerField(default=1)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.nombre} (v{self.version})"

class Alerta(models.Model):
    administrador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alertas')
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.mensaje

class HistorialCambios(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='historial')
    descripcion = models.TextField()
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='cambios_realizados')
    estado_anterior = models.CharField(max_length=20, blank=True, null=True)
    estado_nuevo = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self): return f"Cambio en {self.tramite.nombre} - {self.fecha_cambio}"

class Cita(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='citas')
    empleado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='citas_empleado')
    fecha_hora = models.DateTimeField()
    cancelada = models.BooleanField(default=False)
    def __str__(self): return f"Cita para {self.tramite.nombre} el {self.fecha_hora}"

class Notificacion(models.Model):
    destinatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Notificación para {self.destinatario.email}: {self.mensaje[:20]}..."

class PlantillaDocumento(models.Model):
    nombre = models.CharField(max_length=255, help_text="Título descriptivo de la plantilla.")
    segmento = models.CharField(max_length=100, help_text="Categoría principal, ej: 'Visas', 'Residencias'.")
    tipo_especifico = models.CharField(max_length=150, help_text="Subcategoría, ej: 'Residencia por Inversión'.")
    archivo_base = models.FileField(upload_to='plantillas_maestras/', help_text="Archivo PDF de la plantilla.")
    activo = models.BooleanField(default=True, help_text="Indica si la plantilla está disponible para su uso.")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    administrador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, limit_choices_to={'rol': 'ADMINISTRADOR'}, help_text="Administrador que subió la plantilla.")
    @property
    def url_archivo(self):
        if self.archivo_base: return self.archivo_base.url
        return None
    def __str__(self): return f"{self.nombre} ({self.segmento} - {self.tipo_especifico})"
    class Meta:
        db_table = 'tramites_plantilladocumento'
        verbose_name = "Plantilla de Documento"
        verbose_name_plural = "Plantillas de Documentos"
        ordering = ['-fecha_creacion']

class CampoPlantilla(models.Model):
    TIPO_CAMPO_CHOICES = [('text', 'Texto Corto'), ('textarea', 'Texto Largo'), ('email', 'Correo Electrónico'), ('date', 'Fecha'), ('number', 'Número'), ('checkbox', 'Casilla de Verificación')]
    plantilla = models.ForeignKey(PlantillaDocumento, on_delete=models.CASCADE, related_name='campos')
    seccion = models.CharField(max_length=100, default='Datos Personales', help_text="Sección del formulario a la que pertenece el campo.")
    nombre_campo = models.CharField(max_length=100, help_text="Nombre que verá el usuario (ej: 'Nombre Completo').")
    nombre_tecnico = models.SlugField(max_length=100, help_text="Nombre interno sin espacios (ej: 'nombre_completo').")
    tipo_campo = models.CharField(max_length=20, choices=TIPO_CAMPO_CHOICES)
    es_requerido = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0, help_text="Orden en el que aparecerá el campo en el formulario.")
    def __str__(self): return f"{self.nombre_campo} ({self.tipo_campo}) para {self.plantilla.nombre}"
    class Meta:
        db_table = 'tramites_campoplantilla'
        ordering = ['seccion', 'orden']
        unique_together = ('plantilla', 'nombre_tecnico')

class UltimaAsignacion(models.Model):
    """
    Modelo para rastrear el último empleado asignado y facilitar el algoritmo Round-Robin.
    Solo debería haber un registro en esta tabla.
    """
    ultimo_empleado_id = models.IntegerField(null=True, blank=True, help_text="ID del último empleado asignado")
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Última Asignación"
        verbose_name_plural = "Últimas Asignaciones"
