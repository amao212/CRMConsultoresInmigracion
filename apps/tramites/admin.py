from django.contrib import admin
from .models import PlantillaDocumento, CampoPlantilla

class CampoPlantillaInline(admin.TabularInline):
    """
    Permite editar los campos de una plantilla directamente en la vista de la plantilla.
    'TabularInline' los muestra en un formato de tabla compacto.
    """
    model = CampoPlantilla
    extra = 1  # Muestra 1 campo extra para añadir por defecto.
    fields = ('orden', 'nombre_campo', 'nombre_tecnico', 'tipo_campo', 'es_requerido')
    prepopulated_fields = {'nombre_tecnico': ('nombre_campo',)} # Auto-rellena el nombre técnico

@admin.register(PlantillaDocumento)
class PlantillaDocumentoAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para las Plantillas de Documento.
    """
    list_display = ('nombre', 'segmento', 'tipo_especifico', 'activo', 'fecha_creacion')
    list_filter = ('segmento', 'activo')
    search_fields = ('nombre', 'tipo_especifico')
    inlines = [CampoPlantillaInline] # ¡Aquí es donde ocurre la magia!

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'segmento', 'tipo_especifico', 'activo')
        }),
        ('Archivo y Propietario', {
            'fields': ('archivo_base', 'administrador')
        }),
    )
