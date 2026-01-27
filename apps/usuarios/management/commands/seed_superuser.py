from django.core.management.base import BaseCommand
from apps.usuarios.models import UsuarioCRM

class Command(BaseCommand):
    help = 'Crea un superusuario inicial si no existe'

    def handle(self, *args, **options):
        if not UsuarioCRM.objects.filter(email='admin@admin.com').exists():
            UsuarioCRM.objects.create_superuser(
                email='admin@admin.com',
                password='admin123',
                nombre='Admin General',
                rol='ADMINISTRADOR'
            )
            self.stdout.write(self.style.SUCCESS('Superusuario "admin@admin.com" creado con éxito.'))
        else:
            self.stdout.write(self.style.WARNING('El superusuario "admin@admin.com" ya existe.'))
