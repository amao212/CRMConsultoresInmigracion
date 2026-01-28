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
        
        # Obtener trámites del solicitante
        tramites = Tramite.objects.filter(solicitante=request.user).order_by('-fecha_inicio')
        
        # Separar trámites en curso y finalizados
        estados_finales = ['APROBADO', 'RECHAZADO', 'COMPLETADO']
        tramites_en_curso = []
        tramites_finalizados = []
        
        for tramite in tramites:
            if tramite.estado in estados_finales:
                tramites_finalizados.append(tramite)
            else:
                tramites_en_curso.append(tramite)
        
        # Identificar segmentos bloqueados (trámites activos)
        # Estados activos: PENDIENTE, EN_PROCESO, RETRASADO (asumimos que retrasado también bloquea)
        estados_activos = ['PENDIENTE', 'EN_PROCESO', 'RETRASADO']
        segmentos_bloqueados = set()
        
        # Necesitamos mapear trámite -> segmento. 
        # Como el modelo Tramite no tiene segmento directo, lo inferimos de la plantilla o nombre.
        # Para ser precisos, buscaremos la plantilla asociada al nombre del trámite.
        
        # Optimización: Traer todas las plantillas para mapear nombre -> segmento
        plantillas_all = PlantillaDocumento.objects.all()
        mapa_tramite_segmento = {p.tipo_especifico: p.segmento for p in plantillas_all}
        
        for tramite in tramites:
            if tramite.estado in estados_activos:
                segmento = mapa_tramite_segmento.get(tramite.nombre)
                if segmento:
                    segmentos_bloqueados.add(segmento)
                else:
                    # Fallback si no encuentra plantilla exacta, intentar parsear nombre
                    # (Esto depende de cómo se guarden los nombres, pero es mejor tener el mapa)
                    pass

        plantillas_activas = PlantillaDocumento.objects.filter(activo=True).order_by('segmento', 'tipo_especifico')
        
        menu_plantillas = defaultdict(list)
        tipos_vistos = set() # Para evitar duplicados de tipo_especifico

        for plantilla in plantillas_activas:
            if plantilla.tipo_especifico not in tipos_vistos:
                bloqueado = plantilla.segmento in segmentos_bloqueados
                menu_plantillas[plantilla.segmento].append({
                    'id': plantilla.id,
                    'tipo': plantilla.tipo_especifico,
                    'bloqueado': bloqueado
                })
                tipos_vistos.add(plantilla.tipo_especifico)

        # Obtener el trámite más reciente o activo para el indicador
        tramite_reciente = tramites.first()
        
        context = {
            'user': request.user,
            'menu_plantillas': dict(menu_plantillas),
            'tramites_en_curso': tramites_en_curso,
            'tramites_finalizados': tramites_finalizados,
            'segmentos_bloqueados': list(segmentos_bloqueados),
            'tramite_reciente': tramite_reciente
        }
        return render(request, 'solicitante/dashboard.html', context)
