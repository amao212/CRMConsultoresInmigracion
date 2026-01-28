"""
Comando para crear un tramitador de prueba en el sistema.
"""
from django.core.management.base import BaseCommand
from apps.usuarios.models import UsuarioCRM


class Command(BaseCommand):
    help = 'Crea un tramitador de prueba en el sistema'

    def handle(self, *args, **options):
        # Verificar si ya existe
        email = "tramitador@test.com"
        
        if UsuarioCRM.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'El tramitador {email} ya existe'))
            tramitador = UsuarioCRM.objects.get(email=email)
            
            # Asegurar que esté activo
            if not tramitador.is_active:
                tramitador.is_active = True
                tramitador.save()
                self.stdout.write(self.style.SUCCESS(f'Tramitador {email} activado'))
            
            # Mostrar info
            self.stdout.write(self.style.SUCCESS(f'Email: {tramitador.email}'))
            self.stdout.write(self.style.SUCCESS(f'Nombre: {tramitador.nombre}'))
            self.stdout.write(self.style.SUCCESS(f'Rol: {tramitador.rol}'))
            self.stdout.write(self.style.SUCCESS(f'Activo: {tramitador.is_active}'))
        else:
            # Crear tramitador
            tramitador = UsuarioCRM.objects.create_user(
                email=email,
                password='tramitador123',
                nombre='Tramitador de Prueba',
                rol='TRAMITADOR'
            )
            
            self.stdout.write(self.style.SUCCESS('='*50))
            self.stdout.write(self.style.SUCCESS('✅ Tramitador creado exitosamente'))
            self.stdout.write(self.style.SUCCESS('='*50))
            self.stdout.write(self.style.SUCCESS(f'Email: {tramitador.email}'))
            self.stdout.write(self.style.SUCCESS(f'Contraseña: tramitador123'))
            self.stdout.write(self.style.SUCCESS(f'Nombre: {tramitador.nombre}'))
            self.stdout.write(self.style.SUCCESS(f'Rol: {tramitador.rol}'))
            self.stdout.write(self.style.SUCCESS('='*50))
