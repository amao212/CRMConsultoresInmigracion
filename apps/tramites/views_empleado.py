"""
Vistas para empleados: visualizar trámites asignados, aprobar/rechazar.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, FileResponse, Http404
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.template.loader import render_to_string

from apps.tramites.models import Tramite, Documento, HistorialCambios
from apps.tramites.services.aprobacion_service import AprobacionTramiteService


class EmpleadoDashboardView(LoginRequiredMixin, View):
    """
    Vista del dashboard del empleado con sus trámites asignados.
    """
    def get(self, request):
        # Validar que el usuario sea empleado
        if request.user.rol != 'EMPLEADO':
            messages.error(request, "Solo los empleados pueden acceder a esta página.")
            return redirect(reverse('usuarios:login'))

        # Obtener trámites asignados
        tramites_pendientes = AprobacionTramiteService.obtener_tramites_pendientes(request.user)
        tramites_todos = AprobacionTramiteService.obtener_tramites_asignados(request.user)

        # Estadísticas
        total_asignados = tramites_todos.count()
        total_pendientes = tramites_pendientes.count()
        total_aprobados = tramites_todos.filter(estado='APROBADO').count()
        total_rechazados = tramites_todos.filter(estado='RECHAZADO').count()

        context = {
            'tramites_pendientes': tramites_pendientes,
            'tramites_todos': tramites_todos,
            'total_asignados': total_asignados,
            'total_pendientes': total_pendientes,
            'total_aprobados': total_aprobados,
            'total_rechazados': total_rechazados,
        }

        return render(request, 'empleado/tramites_asignados.html', context)


class DetalleTramiteEmpleadoView(LoginRequiredMixin, View):
    """
    Vista detallada de un trámite para el empleado.
    Muestra el PDF y permite aprobar/rechazar.
    """
    def get(self, request, tramite_id):
        # Validar que el usuario sea empleado
        if request.user.rol != 'EMPLEADO':
            messages.error(request, "Solo los empleados pueden acceder a esta página.")
            return redirect(reverse('usuarios:login'))

        # Obtener el trámite
        tramite = get_object_or_404(
            Tramite.objects.select_related('solicitante', 'empleado_asignado'),
            id=tramite_id
        )

        # Validar que el empleado esté asignado a este trámite
        try:
            AprobacionTramiteService.validar_empleado_asignado(tramite, request.user)
        except PermissionDenied as e:
            messages.error(request, str(e))
            return redirect(reverse('empleado:dashboard'))

        # Obtener el documento más reciente
        documento = tramite.documentos.order_by('-version').first()

        # Obtener historial de cambios
        historial = tramite.historial.select_related('usuario').order_by('-fecha_cambio')

        # DEBUG: Imprimir información
        print(f"DEBUG - Trámite #{tramite.id}")
        print(f"DEBUG - Total documentos: {tramite.documentos.count()}")
        print(f"DEBUG - Documento encontrado: {documento}")

        # Si no hay documento, crear uno de prueba
        if not documento:
            print(f"DEBUG - Creando documento de prueba para trámite #{tramite.id}")
            from apps.tramites.models import Documento
            from django.core.files.base import ContentFile

            # PDF simple de prueba
            pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 88 >>\nstream\nBT\n/F1 18 Tf\n100 700 Td\n(Documento del Tramite) Tj\n0 -30 Td\n(Pendiente de revision) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000314 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n450\n%%EOF"

            documento = Documento(
                tramite=tramite,
                nombre=tramite.nombre,
                version=1
            )

            # Guardar archivo
            id_formateado = f"solicitante_{tramite.solicitante.id:04d}"
            tipo_limpio = tramite.nombre.lower().replace(' ', '_')
            nombre_archivo = f"{tipo_limpio}_v1.pdf"
            ruta_archivo = f"solicitante/{id_formateado}/visas/{nombre_archivo}"

            documento.archivo.save(ruta_archivo, ContentFile(pdf_content), save=True)
            print(f"DEBUG - Documento creado: {documento.archivo.name}")

        context = {
            'tramite': tramite,
            'documento': documento,
            'historial': historial,
            'puede_aprobar_rechazar': tramite.estado == 'PENDIENTE',
        }

        return render(request, 'empleado/detalle_tramite.html', context)


class AprobarTramiteView(LoginRequiredMixin, View):
    """
    Vista para aprobar un trámite.
    """
    def post(self, request, tramite_id):
        # Validar que el usuario sea empleado
        if request.user.rol != 'EMPLEADO':
            return JsonResponse({'error': 'Solo los empleados pueden aprobar trámites.'}, status=403)

        try:
            tramite = AprobacionTramiteService.aprobar_tramite(tramite_id, request.user)
            messages.success(request, f"Trámite '{tramite.nombre}' aprobado exitosamente.")
            return redirect(reverse('empleado:detalle-tramite', kwargs={'tramite_id': tramite_id}))
        except PermissionDenied as e:
            messages.error(request, str(e))
            return redirect(reverse('empleado:dashboard'))
        except Exception as e:
            messages.error(request, f"Error al aprobar el trámite: {e}")
            return redirect(reverse('empleado:detalle-tramite', kwargs={'tramite_id': tramite_id}))


class RechazarTramiteView(LoginRequiredMixin, View):
    """
    Vista para rechazar un trámite.
    """
    def post(self, request, tramite_id):
        # Validar que el usuario sea empleado
        if request.user.rol != 'EMPLEADO':
            return JsonResponse({'error': 'Solo los empleados pueden rechazar trámites.'}, status=403)

        motivo = request.POST.get('motivo_rechazo', '').strip()

        if not motivo:
            messages.error(request, "Debe proporcionar un motivo para rechazar el trámite.")
            return redirect(reverse('empleado:detalle-tramite', kwargs={'tramite_id': tramite_id}))

        try:
            tramite = AprobacionTramiteService.rechazar_tramite(tramite_id, request.user, motivo)
            messages.success(request, f"Trámite '{tramite.nombre}' rechazado.")
            return redirect(reverse('empleado:detalle-tramite', kwargs={'tramite_id': tramite_id}))
        except PermissionDenied as e:
            messages.error(request, str(e))
            return redirect(reverse('empleado:dashboard'))
        except Exception as e:
            messages.error(request, f"Error al rechazar el trámite: {e}")
            return redirect(reverse('empleado:detalle-tramite', kwargs={'tramite_id': tramite_id}))


class VisualizarPDFTramiteView(LoginRequiredMixin, View):
    """
    Vista para visualizar el PDF de un trámite.
    Solo el empleado asignado puede ver el PDF.
    """
    def get(self, request, tramite_id):
        # Validar que el usuario sea empleado
        if request.user.rol != 'EMPLEADO':
            raise Http404("No tiene permiso para ver este documento.")

        # Obtener el trámite
        tramite = get_object_or_404(
            Tramite.objects.select_related('empleado_asignado'),
            id=tramite_id
        )

        # Validar que el empleado esté asignado
        try:
            AprobacionTramiteService.validar_empleado_asignado(tramite, request.user)
        except PermissionDenied:
            raise Http404("No tiene permiso para ver este documento.")

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

class EstadoTramiteAPIView(LoginRequiredMixin, View):
    """
    API para obtener el estado actual de un trámite (polling).
    """
    def get(self, request, tramite_id):
        if request.user.rol != 'EMPLEADO':
            return JsonResponse({'error': 'No autorizado'}, status=403)
            
        tramite = get_object_or_404(Tramite, id=tramite_id)
        
        # Validar asignación
        if tramite.empleado_asignado != request.user:
            return JsonResponse({'error': 'No autorizado'}, status=403)
            
        # Obtener el historial completo
        historial = tramite.historial.select_related('usuario').order_by('-fecha_cambio')
        ultimo_cambio = historial.first()
        
        # Renderizar parciales
        badge_html = render_to_string('empleado/partials/estado_badge.html', {'estado': tramite.estado})
        timeline_html = render_to_string('empleado/partials/historial_timeline.html', {'historial': historial})
        
        data = {
            'estado': tramite.estado,
            'estado_display': tramite.get_estado_display(),
            'ultima_actualizacion': ultimo_cambio.fecha_cambio.isoformat() if ultimo_cambio else tramite.fecha_inicio.isoformat(),
            'usuario_modificacion': ultimo_cambio.usuario.nombre if ultimo_cambio and ultimo_cambio.usuario else 'Sistema',
            'badge_html': badge_html,
            'timeline_html': timeline_html
        }
        
        return JsonResponse(data)

class HistorialGeneralView(LoginRequiredMixin, View):
    """
    Vista para ver el historial general de cambios de todos los trámites asignados.
    """
    def get(self, request):
        if request.user.rol != 'EMPLEADO':
            messages.error(request, "Solo los empleados pueden acceder a esta página.")
            return redirect(reverse('usuarios:login'))

        # Obtener historial de todos los trámites asignados al empleado
        historial = HistorialCambios.objects.filter(
            tramite__empleado_asignado=request.user
        ).select_related('tramite', 'tramite__solicitante', 'usuario').order_by('-fecha_cambio')

        context = {
            'historial': historial
        }

        return render(request, 'empleado/historial_general.html', context)
