from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.template.loader import render_to_string
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from collections import defaultdict

from .models import PlantillaDocumento, CampoPlantilla, Tramite, Documento, HistorialCambios
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
            archivos = request.FILES.getlist('archivos')

            if archivos:
                try:
                    nuevo_tramite = iniciar_nuevo_tramite(request.user, plantilla, {})
                    doc_generado = Documento.objects.filter(tramite=nuevo_tramite).first()
                    if doc_generado:
                        doc_generado.delete()

                    documentos_guardados = 0

                    for archivo in archivos:
                        guardar_documento(nuevo_tramite, archivo)
                        documentos_guardados += 1

                    return redirect(reverse('usuarios:dashboard-solicitante'))

                except Exception as e:
                    messages.error(request, f"Error al iniciar el trámite: {e}")
                    return redirect(reverse('usuarios:dashboard-solicitante'))
            else:
                messages.error(request, "Debe seleccionar al menos un archivo PDF.")
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
    Ahora refactorizada para mostrar historial consolidado por tipo de trámite.
    """
    def get(self, request, tramite_id):
        if request.user.rol != 'SOLICITANTE':
            messages.error(request, "Acceso denegado.")
            return redirect(reverse('usuarios:login'))

        # Obtener el trámite solicitado
        tramite_actual = get_object_or_404(Tramite, id=tramite_id, solicitante=request.user)
        
        # Agrupar trámites del mismo tipo (nombre) para este solicitante
        # Esto permite ver el historial completo de "Visa de aplicación", por ejemplo, aunque sean varios registros
        tramites_tipo = Tramite.objects.filter(
            solicitante=request.user,
            nombre=tramite_actual.nombre
        ).order_by('-fecha_inicio')
        
        # Consolidar historial de cambios de todos los trámites de este tipo
        historial_consolidado = HistorialCambios.objects.filter(
            tramite__in=tramites_tipo
        ).select_related('tramite', 'usuario').order_by('-fecha_cambio')
        
        # Obtener documentos de todos los trámites de este tipo
        documentos_consolidado = Documento.objects.filter(
            tramite__in=tramites_tipo
        ).select_related('tramite').order_by('-fecha_subida')
        
        # Intentar obtener la plantilla asociada (usando el trámite más reciente o el actual)
        plantilla = None
        try:
            plantilla = PlantillaDocumento.objects.filter(tipo_especifico=tramite_actual.nombre, activo=True).first()
        except Exception:
            pass

        # Formulario para subir documento (se asocia al trámite actual/más reciente activo)
        # Si el trámite actual está finalizado, quizás deberíamos bloquear la subida o crear uno nuevo,
        # pero por ahora mantenemos la lógica de subir al trámite actual si no está cerrado, o al último.
        # Para simplificar, usamos el tramite_id que llegó en la URL.
        form = SubirDocumentoForm()
        # Determinar si mostrar opción de subida (solo si el trámite actual está en estado final)
        # REQUISITO: La sección “Gestión de Documentos” debe mostrarse solo si el trámite está FINALIZADO (APROBADO, RECHAZADO).
        # Si está en curso (PENDIENTE, EN_PROCESO, etc.), NO debe mostrarse.
        
        # estados_finales = ['APROBADO', 'RECHAZADO']
        # mostrar_gestion_documentos = tramite_actual.estado in estados_finales
        
        # NUEVO REQUISITO: "en ningun historial de tramite en la pantalla del solicitante, no debe salir la parte de gestión de documento"
        # Esto significa que NUNCA se debe mostrar la gestión de documentos en esta vista.
        mostrar_gestion_documentos = False

        # --- Logic added to populate the sidebar (same as Dashboard) ---
        # 1. Get all tramites for the user to calculate status/menu
        all_tramites = Tramite.objects.filter(solicitante=request.user).order_by('-fecha_inicio')
        
        # 2. Identify blocked segments
        estados_activos = ['PENDIENTE', 'EN_PROCESO', 'RETRASADO']
        segmentos_bloqueados = set()
        plantillas_all = PlantillaDocumento.objects.all()
        mapa_tramite_segmento = {p.tipo_especifico: p.segmento for p in plantillas_all}
        
        for t in all_tramites:
            if t.estado in estados_activos:
                segmento = mapa_tramite_segmento.get(t.nombre)
                if segmento:
                    segmentos_bloqueados.add(segmento)

        # 3. Build the menu
        plantillas_activas = PlantillaDocumento.objects.filter(activo=True).order_by('segmento', 'tipo_especifico')
        menu_plantillas = defaultdict(list)
        tipos_vistos = set()

        for p in plantillas_activas:
            if p.tipo_especifico not in tipos_vistos:
                bloqueado = p.segmento in segmentos_bloqueados
                menu_plantillas[p.segmento].append({
                    'id': p.id,
                    'tipo': p.tipo_especifico,
                    'bloqueado': bloqueado
                })
                tipos_vistos.add(p.tipo_especifico)

        # 4. Get recent tramite for the spinner
        tramite_reciente = all_tramites.first()
        # ---------------------------------------------------------------

        context = {
            'tramite': tramite_actual, # Trámite principal/actual
            'tramites_tipo': tramites_tipo, # Lista de trámites del mismo tipo
            'historial': historial_consolidado,
            'documentos': documentos_consolidado,
            'plantilla': plantilla,
            'form': form,
            'mostrar_gestion_documentos': mostrar_gestion_documentos,
            'menu_plantillas': dict(menu_plantillas),
            'tramite_reciente': tramite_reciente,
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
            # Obtener múltiples archivos desde request.FILES
            archivos = request.FILES.getlist('archivos')

            if archivos:
                try:
                    documentos_guardados = 0

                    for archivo in archivos:
                        # Guardar el documento
                        guardar_documento(tramite, archivo)
                        documentos_guardados += 1


                except Exception as e:
                    messages.error(request, f"Error al subir documentos: {e}")
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

class VisualizarDocumentoEspecificoView(LoginRequiredMixin, View):
    """
    Vista para visualizar un documento específico por su ID.
    Valida que el documento pertenezca a un trámite del solicitante.
    """
    def get(self, request, documento_id):
        if request.user.rol != 'SOLICITANTE':
            raise PermissionDenied("Acceso denegado.")

        documento = get_object_or_404(Documento, id=documento_id)
        
        # Validar que el trámite pertenezca al usuario
        if documento.tramite.solicitante != request.user:
            raise PermissionDenied("No tiene permiso para ver este documento.")

        try:
            return FileResponse(
                documento.archivo.open('rb'),
                content_type='application/pdf',
                as_attachment=False,
                filename=f"{documento.nombre}_v{documento.version}.pdf"
            )
        except Exception as e:
            raise Http404(f"Error al abrir el documento: {e}")
