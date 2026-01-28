from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.template.loader import render_to_string
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from collections import defaultdict

from .models import PlantillaDocumento, CampoPlantilla, Tramite, Documento
from .services import iniciar_nuevo_tramite, actualizar_datos_tramite, TramiteDataService
from .services.storage_service import guardar_documento
from .forms import SubirDocumentoForm

class GenerarFormularioPlantillaView(LoginRequiredMixin, View):
    """
    Vista que genera y devuelve un formulario HTML dinámicamente
    basado en los CampoPlantilla asociados a una PlantillaDocumento, agrupados por sección.
    """
    def get(self, request, plantilla_id):
        plantilla = get_object_or_404(PlantillaDocumento, id=plantilla_id, activo=True)
        
        # Validación de bloqueo de segmento
        # Verificar si el usuario ya tiene un trámite activo en este segmento
        estados_activos = ['PENDIENTE', 'EN_PROCESO', 'RETRASADO']
        
        # Buscar trámites activos del usuario
        tramites_activos = Tramite.objects.filter(
            solicitante=request.user,
            estado__in=estados_activos
        )
        
        # Verificar si alguno pertenece al mismo segmento que la plantilla solicitada
        # Necesitamos saber el segmento de los trámites activos.
        # Podemos hacerlo buscando las plantillas correspondientes a esos trámites.
        
        segmento_bloqueado = False
        for tramite in tramites_activos:
            # Intentar encontrar la plantilla del trámite activo para saber su segmento
            # Asumimos que tramite.nombre coincide con plantilla.tipo_especifico
            plantilla_tramite = PlantillaDocumento.objects.filter(tipo_especifico=tramite.nombre).first()
            if plantilla_tramite and plantilla_tramite.segmento == plantilla.segmento:
                segmento_bloqueado = True
                break
        
        if segmento_bloqueado:
             # Si es una petición AJAX, devolver error JSON, si no, redirigir
             if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                 return JsonResponse({'error': 'Ya tienes un trámite en curso en este segmento.'}, status=403)
             else:
                 messages.error(request, 'Ya tienes un trámite en curso en este segmento.')
                 return redirect('usuarios:dashboard-solicitante')

        
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
        
        # Validación de bloqueo de segmento (Backend Check)
        estados_activos = ['PENDIENTE', 'EN_PROCESO', 'RETRASADO']
        tramites_activos = Tramite.objects.filter(
            solicitante=request.user,
            estado__in=estados_activos
        )
        
        for tramite in tramites_activos:
            plantilla_tramite = PlantillaDocumento.objects.filter(tipo_especifico=tramite.nombre).first()
            if plantilla_tramite and plantilla_tramite.segmento == plantilla.segmento:
                messages.error(request, 'No puedes iniciar este trámite porque ya tienes uno en curso en el mismo segmento.')
                return redirect(reverse('usuarios:dashboard-solicitante'))

        
        # En este flujo modificado, el formulario de inicio de trámite es en realidad
        # la subida del primer documento (plantilla llenada).
        
        form = SubirDocumentoForm(request.POST, request.FILES)
        
        if form.is_valid():
            archivo = form.cleaned_data['archivo']
            try:
                # 1. Crear el trámite básico (sin datos de formulario JSON por ahora)
                # Usamos un diccionario vacío para form_data ya que los datos están en el PDF
                nuevo_tramite = iniciar_nuevo_tramite(request.user, plantilla, {})
                
                # 2. Guardar el documento subido asociado al trámite
                # Esto sobrescribirá o complementará lo que hace iniciar_nuevo_tramite
                # (iniciar_nuevo_tramite actualmente genera un PDF vacío/relleno, aquí subimos el real)
                
                # Nota: iniciar_nuevo_tramite ya crea un documento inicial. 
                # Podríamos refactorizar iniciar_nuevo_tramite para aceptar un archivo inicial,
                # pero para minimizar cambios, dejaremos que cree el trámite y luego subimos el documento.
                
                # Sin embargo, iniciar_nuevo_tramite intenta rellenar un PDF. 
                # Si pasamos form_data vacío, generará un PDF con campos vacíos.
                # Lo ideal es que el archivo subido sea el v1.
                
                # Ajuste: Vamos a usar guardar_documento para subir el archivo real.
                # Como iniciar_nuevo_tramite ya crea un v1, este será v2, o podemos reemplazarlo.
                # Para simplificar y cumplir el requisito "v1", lo mejor sería modificar iniciar_nuevo_tramite
                # o manejarlo aquí manualmente.
                
                # Estrategia: Dejar que iniciar_nuevo_tramite haga su trabajo (creará v1 generado).
                # Luego subimos el archivo del usuario como v2 (o v1 si logramos interceptarlo).
                # Dado que el usuario sube SU versión llenada, esa debería ser la válida.
                
                # Para cumplir estrictamente "v1" al subir:
                # Vamos a eliminar el documento generado automáticamente si existe y subir el del usuario.
                
                doc_generado = Documento.objects.filter(tramite=nuevo_tramite).first()
                if doc_generado:
                    doc_generado.delete() # Borramos el generado por el sistema
                    
                # Ahora guardamos el subido por el usuario. Al no haber docs, será v1.
                guardar_documento(nuevo_tramite, archivo)
                
                messages.success(request, f"Trámite '{nuevo_tramite.nombre}' iniciado con éxito. Documento subido correctamente.")
                return redirect(reverse('usuarios:dashboard-solicitante'))
                
            except Exception as e:
                messages.error(request, f"Error al iniciar el trámite: {e}")
                return redirect(reverse('usuarios:dashboard-solicitante'))
        else:
             messages.error(request, "Error en el archivo subido. Asegúrese de que es un PDF válido y menor a 10MB.")
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

class DetalleTramiteSolicitanteView(LoginRequiredMixin, View):
    """
    Vista para que el solicitante vea el detalle de su trámite, descargue la plantilla y suba el PDF llenado.
    """
    def get(self, request, tramite_id):
        if request.user.rol != 'SOLICITANTE':
            messages.error(request, "Acceso denegado.")
            return redirect(reverse('usuarios:login'))

        tramite = get_object_or_404(Tramite, id=tramite_id, solicitante=request.user)
        
        # Intentar obtener la plantilla asociada
        plantilla = None
        try:
            plantilla = PlantillaDocumento.objects.filter(tipo_especifico=tramite.nombre, activo=True).first()
        except Exception:
            pass

        # Obtener el último documento subido (si existe)
        ultimo_documento = Documento.objects.filter(tramite=tramite).order_by('-version').first()
        
        form = SubirDocumentoForm()

        context = {
            'tramite': tramite,
            'plantilla': plantilla,
            'ultimo_documento': ultimo_documento,
            'form': form,
        }
        return render(request, 'tramites/detalle_tramite_solicitante.html', context)

    def post(self, request, tramite_id):
        if request.user.rol != 'SOLICITANTE':
            messages.error(request, "Acceso denegado.")
            return redirect(reverse('usuarios:login'))

        tramite = get_object_or_404(Tramite, id=tramite_id, solicitante=request.user)
        
        # Intentar obtener la plantilla asociada para pasarla al storage service
        try:
            plantilla = PlantillaDocumento.objects.filter(tipo_especifico=tramite.nombre, activo=True).first()
            if plantilla:
                tramite.plantilla = plantilla
        except Exception:
            pass

        form = SubirDocumentoForm(request.POST, request.FILES)
        
        if form.is_valid():
            archivo = form.cleaned_data['archivo']
            try:
                guardar_documento(tramite, archivo)
                messages.success(request, "Documento subido exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al subir el documento: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        return redirect(reverse('tramites:detalle_tramite', args=[tramite_id]))

class DescargarPlantillaView(LoginRequiredMixin, View):
    """
    Permite descargar la plantilla PDF maestra asociada a un trámite.
    """
    def get(self, request, tramite_id):
        if request.user.rol != 'SOLICITANTE':
            raise PermissionDenied("Solo solicitantes.")

        tramite = get_object_or_404(Tramite, id=tramite_id, solicitante=request.user)
        plantilla = get_object_or_404(PlantillaDocumento, tipo_especifico=tramite.nombre, activo=True)

        if not plantilla.archivo_base:
            messages.error(request, "No hay archivo base para esta plantilla.")
            return redirect(reverse('tramites:detalle_tramite', args=[tramite_id]))

        response = HttpResponse(plantilla.archivo_base, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{plantilla.nombre}.pdf"'
        return response


class VisualizarPDFSolicitanteView(LoginRequiredMixin, View):
    """
    Vista para que el solicitante visualice el PDF de su trámite en el navegador.
    """
    def get(self, request, tramite_id):
        if request.user.rol != 'SOLICITANTE':
            raise Http404("No tiene permiso para ver este documento.")

        tramite = get_object_or_404(Tramite, id=tramite_id, solicitante=request.user)

        # Obtener el documento más reciente
        documento = tramite.documentos.order_by('-version').first()

        if not documento or not documento.archivo:
            raise Http404("No se encontró el documento.")

        try:
            # Retornar el archivo PDF
            return FileResponse(
                documento.archivo.open('rb'),
                content_type='application/pdf',
                as_attachment=False,  # Mostrar en el navegador, no descargar
                filename=f"{tramite.nombre}_v{documento.version}.pdf"
            )
        except Exception as e:
            raise Http404(f"Error al abrir el documento: {e}")

