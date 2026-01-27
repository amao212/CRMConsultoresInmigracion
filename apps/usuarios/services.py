from .models import UsuarioCRM
from django.contrib.auth.hashers import make_password

def crear_empleado(nombre, email, password, rol):
    """
    Crea un nuevo empleado en el sistema.
    """
    if not nombre or not email or not password or not rol:
        raise ValueError("Todos los campos son requeridos.")

    if UsuarioCRM.objects.filter(email=email).exists():
        raise ValueError("El email ya está registrado.")

    user = UsuarioCRM.objects.create(
        nombre=nombre,
        email=email,
        password=make_password(password), # Hashea la contraseña
        rol=rol
    )
    return user
