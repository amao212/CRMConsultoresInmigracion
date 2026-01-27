from .models import UsuarioCRM

def get_all_empleados():
    """
    Retorna todos los usuarios que no son solicitantes.
    """
    return UsuarioCRM.objects.filter(rol__in=['ADMINISTRADOR', 'EMPLEADO']).order_by('-fecha_creacion')
