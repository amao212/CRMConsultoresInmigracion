from .models import UsuarioCRM

def get_all_tramitadores():
    """
    Retorna todos los usuarios que no son solicitantes.
    """
    return UsuarioCRM.objects.filter(rol__in=['ADMINISTRADOR', 'TRAMITADOR']).order_by('-fecha_creacion')
