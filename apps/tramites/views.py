from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from collections import defaultdict

from .models import PlantillaDocumento, CampoPlantilla, Tramite
from .services import iniciar_nuevo_tramite, actualizar_datos_tramite, TramiteDataService

class GenerarFormularioPlantillaView(LoginRequiredMixin, View):
    """
    Vista que genera y devuelve un formulario HTML dinámicamente
    basado en los CampoPlantilla asociados a una PlantillaDocumento, agrupados por sección.
    """
    def get(self, request, plantilla_id):
        plantilla = get_object_or_404(PlantillaDocumento, id=plantilla_id, activo=True)
        
        # Agrupar campos por sección
        campos_por_seccion = defaultdict(list)
        for campo in plantilla.campos.all().order_by('seccion', 'orden'):
            campos_por_seccion[campo.seccion].append(campo)

        form_html = render_to_string('tramites/formulario_dinamico.html', {
            'plantilla': plantilla,
            'campos_por_seccion': dict(campos_por_seccion), # Pasar el diccionario agrupado
            'user': request.user
        }, request=request)

        return JsonResponse({'form_html': form_html, 'plantilla_nombre': plantilla.nombre})


class IniciarTramiteView(LoginRequiredMixin, View):
    """
    Vista para iniciar un nuevo trámite a partir de una plantilla y los datos del solicitante.
    """
    def post(self, request, plantilla_id):
        if request.user.rol != 'SOLICITANTE':
            messages.error(request, "Solo los solicitantes pueden iniciar trámites.")
            return redirect(reverse('usuarios:login'))

        plantilla = get_object_or_404(PlantillaDocumento, id=plantilla_id, activo=True)
        
        form_data = {key: value for key, value in request.POST.items() if key != 'csrfmiddlewaretoken'}

        try:
            nuevo_tramite = iniciar_nuevo_tramite(request.user, plantilla, form_data)
            messages.success(request, f"Trámite '{nuevo_tramite.nombre}' iniciado con éxito. Se ha generado el documento inicial.")
            return redirect(reverse('usuarios:dashboard-solicitante'))
        except Exception as e:
            messages.error(request, f"Error al iniciar el trámite: {e}")
            return redirect(reverse('usuarios:dashboard-solicitante'))


class ActualizarTramiteView(LoginRequiredMixin, View):
    """
    Vista para actualizar los datos de un trámite existente.
    Solo el solicitante propietario puede actualizar sus trámites.
    """
    def get(self, request, tramite_id):
        if request.user.rol != 'SOLICITANTE':
            messages.error(request, "Solo los solicitantes pueden actualizar trámites.")
            return redirect(reverse('usuarios:login'))

        try:
            datos_actuales = TramiteDataService.obtener_datos_tramite(tramite_id, request.user)

            tramite = Tramite.objects.get(id=tramite_id)
            plantilla = PlantillaDocumento.objects.get(tipo_especifico=tramite.nombre, activo=True)
            
            # Agrupar campos por sección para la edición
            campos_por_seccion = defaultdict(list)
            for campo in plantilla.campos.all().order_by('seccion', 'orden'):
                campos_por_seccion[campo.seccion].append(campo)

            form_html = render_to_string('tramites/formulario_dinamico.html', {
                'plantilla': plantilla,
                'campos_por_seccion': dict(campos_por_seccion), # Pasar el diccionario agrupado
                'datos_actuales': datos_actuales,
                'tramite_id': tramite_id,
                'user': request.user
            }, request=request)

            return JsonResponse({
                'form_html': form_html,
                'plantilla_nombre': plantilla.nombre,
                'tramite_id': tramite_id
            })

        except PermissionDenied as e:
            return JsonResponse({'error': str(e)}, status=403)
        except Exception as e:
            return JsonResponse({'error': f'Error al cargar el trámite: {e}'}, status=400)

    def post(self, request, tramite_id):
        if request.user.rol != 'SOLICITANTE':
            messages.error(request, "Solo los solicitantes pueden actualizar trámites.")
            return redirect(reverse('usuarios:login'))

        form_data = {key: value for key, value in request.POST.items() if key != 'csrfmiddlewaretoken'}

        try:
            tramite_actualizado = actualizar_datos_tramite(tramite_id, request.user, form_data)
            messages.success(request, f"Trámite '{tramite_actualizado.nombre}' actualizado con éxito. Se ha generado una nueva versión del documento.")
            return redirect(reverse('usuarios:dashboard-solicitante'))
        except PermissionDenied as e:
            messages.error(request, f"Permiso denegado: {e}")
            return redirect(reverse('usuarios:dashboard-solicitante'))
        except Exception as e:
            messages.error(request, f"Error al actualizar el trámite: {e}")
            return redirect(reverse('usuarios:dashboard-solicitante'))
