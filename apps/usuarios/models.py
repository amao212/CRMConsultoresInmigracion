from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UsuarioCRMManager(BaseUserManager):
    """
    Manager for the custom user model, using email as the unique identifier.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'ADMINISTRADOR')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class UsuarioCRM(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for the CRM.
    """
    ROL_CHOICES = (
        ('ADMINISTRADOR', 'Administrador'),
        ('EMPLEADO', 'Empleado'),
        ('SOLICITANTE', 'Solicitante'),
    )

    email = models.EmailField(unique=True, help_text="Email address will be used as the username.")
    nombre = models.CharField(max_length=150, blank=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False, help_text="Designates whether the user can log into the admin site.")
    
    fecha_creacion = models.DateTimeField(default=timezone.now)

    objects = UsuarioCRMManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.email
