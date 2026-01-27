from .models import PlantillaDocumento

def get_all_plantillas():
    """
    Retorna todas las plantillas de documentos ordenadas por fecha de creación.
    """
    return PlantillaDocumento.objects.all().order_by('-fecha_creacion')
