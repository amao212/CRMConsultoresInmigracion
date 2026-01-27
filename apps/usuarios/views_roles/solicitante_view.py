from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from apps.tramites.models import PlantillaDocumento, Tramite
from collections import defaultdict
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

@method_decorator(never_cache, name='dispatch')
class SolicitanteDashboardView(LoginRequiredMixin, View):
    """
    Vista para el panel de control del solicitante.
    """
    login_url = '/usuarios/login/'

    def get(self, request):
        if request.user.rol != 'SOLICITANTE':
            return redirect(reverse('usuarios:login'))
        
        plantillas_activas = PlantillaDocumento.objects.filter(activo=True).order_by('segmento', 'tipo_especifico')
        
        menu_plantillas = defaultdict(list)
        tipos_vistos = set() # Para evitar duplicados de tipo_especifico

        for plantilla in plantillas_activas:
            # Usamos un set para no mostrar el mismo tipo de trámite dos veces
            # aunque haya varias plantillas con el mismo nombre.
            if plantilla.tipo_especifico not in tipos_vistos:
                menu_plantillas[plantilla.segmento].append({
                    'id': plantilla.id,
                    'tipo': plantilla.tipo_especifico
                })
                tipos_vistos.add(plantilla.tipo_especifico)

        # Obtener trámites del solicitante
        tramites = Tramite.objects.filter(solicitante=request.user).order_by('-fecha_inicio')

        context = {
            'user': request.user,
            'menu_plantillas': dict(menu_plantillas),
            'tramites': tramites,
        }
        return render(request, 'solicitante/dashboard.html', context)
