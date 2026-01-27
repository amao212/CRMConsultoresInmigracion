from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from django.urls import reverse
from apps.usuarios.models import UsuarioCRM

class RegistroView(View):
    """
    Gestiona el registro de nuevos usuarios con el rol de 'SOLICITANTE'.
    """
    template_name = 'registro.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            return render(request, self.template_name, {'error': 'Las contraseñas no coinciden.'})
        
        if UsuarioCRM.objects.filter(email=email).exists():
            return render(request, self.template_name, {'error': 'El correo electrónico ya está en uso.'})

        try:
            user = UsuarioCRM.objects.create_user(
                email=email,
                password=password,
                nombre=nombre,
                rol='SOLICITANTE'
            )
            
            login(request, user)
            
            # Redirigir al nuevo dashboard del solicitante
            return redirect(reverse('usuarios:dashboard-solicitante'))

        except Exception as e:
            return render(request, self.template_name, {'error': f'Ocurrió un error durante el registro: {e}'})
