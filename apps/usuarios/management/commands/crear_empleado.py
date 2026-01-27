"""
Comando para crear un empleado de prueba en el sistema.
"""
from django.core.management.base import BaseCommand
from apps.usuarios.models import UsuarioCRM


class Command(BaseCommand):
    help = 'Crea un empleado de prueba en el sistema'

    def handle(self, *args, **options):
        # Verificar si ya existe
        email = "empleado@test.com"
        
        if UsuarioCRM.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'El empleado {email} ya existe'))
            empleado = UsuarioCRM.objects.get(email=email)
            
            # Asegurar que esté activo
            if not empleado.activo:
                empleado.activo = True
                empleado.save()
                self.stdout.write(self.style.SUCCESS(f'Empleado {email} activado'))
            
            # Mostrar info
            self.stdout.write(self.style.SUCCESS(f'Email: {empleado.email}'))
            self.stdout.write(self.style.SUCCESS(f'Nombre: {empleado.nombre}'))
            self.stdout.write(self.style.SUCCESS(f'Rol: {empleado.rol}'))
            self.stdout.write(self.style.SUCCESS(f'Activo: {empleado.activo}'))
        else:
            # Crear empleado
            empleado = UsuarioCRM.objects.create_user(
                email=email,
                password='empleado123',
                nombre='Empleado de Prueba',
                rol='EMPLEADO'
            )
            
            self.stdout.write(self.style.SUCCESS('='*50))
            self.stdout.write(self.style.SUCCESS('✅ Empleado creado exitosamente'))
            self.stdout.write(self.style.SUCCESS('='*50))
            self.stdout.write(self.style.SUCCESS(f'Email: {empleado.email}'))
            self.stdout.write(self.style.SUCCESS(f'Contraseña: empleado123'))
            self.stdout.write(self.style.SUCCESS(f'Nombre: {empleado.nombre}'))
            self.stdout.write(self.style.SUCCESS(f'Rol: {empleado.rol}'))
            self.stdout.write(self.style.SUCCESS('='*50))
