from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

class LoginView(View):
    """
    Gestiona la autenticación de usuarios y la redirección basada en roles.
    """
    template_name = 'login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return self._redirect_user(request.user)
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return self._redirect_user(user)
        else:
            context = {'error': 'Credenciales inválidas. Por favor, inténtalo de nuevo.'}
            return render(request, self.template_name, context)

    def _redirect_user(self, user):
        """Redirige al usuario según su rol después de un inicio de sesión exitoso."""
        if user.rol == 'ADMINISTRADOR':
            return redirect(reverse('usuarios:dashboard-admin'))
        elif user.rol == 'TRAMITADOR':
            return redirect(reverse('tramitador:dashboard'))  # Nueva vista con trámites asignados
        elif user.rol == 'SOLICITANTE':
            return redirect(reverse('usuarios:dashboard-solicitante'))
        
        # Redirección por defecto si el rol no tiene un dashboard específico
        return redirect(reverse('usuarios:login'))

class LogoutView(View):
    """
    Gestiona el cierre de sesión del usuario.
    """
    def get(self, request):
        logout(request)
        return redirect(reverse('usuarios:login'))
