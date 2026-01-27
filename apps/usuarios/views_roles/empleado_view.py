from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

@method_decorator(never_cache, name='dispatch')
class EmpleadoDashboardView(LoginRequiredMixin, View):
    """
    Vista para el panel de control del empleado.
    Requiere autenticación y rol de 'EMPLEADO'.
    """
    login_url = '/usuarios/login/' # Si no está logueado, va al login

    def get(self, request):
        # Verificamos que el usuario sea un empleado
        if request.user.rol != 'EMPLEADO':
            # Si no lo es, lo redirigimos a la pantalla de login para evitar accesos no autorizados
            return redirect(reverse('usuarios:login'))
        
        # Si es un empleado, renderizamos su dashboard
        context = {
            'user': request.user
        }
        return render(request, 'empleado/dashboard.html', context)
