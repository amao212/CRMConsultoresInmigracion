from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import FileResponse, Http404
from apps.usuarios.models import UsuarioCRM
from apps.tramites.selectors import get_all_plantillas
from apps.tramites.services.storage_service import crear_plantilla_documento, eliminar_plantilla_documento
from apps.tramites.models import PlantillaDocumento, Tramite, Documento

@method_decorator(never_cache, name='dispatch')
class AdminDashboardView(LoginRequiredMixin, View):
    """
    Vista para el panel de control del administrador.
    Requiere autenticación y rol de 'ADMINISTRADOR'.
    """
    def get(self, request):
        # Verificar si el usuario tiene el rol correcto
        if request.user.rol != 'ADMINISTRADOR':
            return redirect('usuarios:login')

        # Estadísticas del dashboard
        total_usuarios = UsuarioCRM.objects.count()
        total_tramitadores = UsuarioCRM.objects.filter(rol='TRAMITADOR').count()
        total_administradores = UsuarioCRM.objects.filter(rol='ADMINISTRADOR').count()

        context = {
            'user': request.user,
            'total_usuarios': total_usuarios,
            'total_tramitadores': total_tramitadores,
            'total_administradores': total_administradores,
        }
        return render(request, 'administrador/dashboard.html', context)


@method_decorator(never_cache, name='dispatch')
class GestionTramitadoresView(LoginRequiredMixin, View):
    """
    Vista para gestionar tramitadores y administradores (CRUD completo).
    """
    def get(self, request):
        if request.user.rol != 'ADMINISTRADOR':
            return redirect('usuarios:login')

        # Obtener tramitadores y administradores (excluyendo al usuario actual)
        tramitadores = UsuarioCRM.objects.filter(rol='TRAMITADOR').order_by('-fecha_creacion')
        administradores = UsuarioCRM.objects.filter(rol='ADMINISTRADOR').exclude(id=request.user.id).order_by('-fecha_creacion')

        context = {
            'user': request.user,
            'tramitadores': tramitadores,
            'administradores': administradores,
        }
        return render(request, 'administrador/usuarios.html', context)


@method_decorator(never_cache, name='dispatch')
class CrearUsuarioView(LoginRequiredMixin, View):
    """
    Vista para crear nuevos usuarios (tramitadores o solicitantes).
    """
    def get(self, request):
        if request.user.rol != 'ADMINISTRADOR':
            return redirect('usuarios:login')

        context = {'user': request.user}
        return render(request, 'administrador/crear_usuario.html', context)

    def post(self, request):
        if request.user.rol != 'ADMINISTRADOR':
            return redirect('usuarios:login')

        try:
            nombre = request.POST.get('nombre')
            email = request.POST.get('email')
            password = request.POST.get('password')
            rol = request.POST.get('rol')

            # Validar datos
            if not all([nombre, email, password, rol]):
                messages.error(request, 'Todos los campos son obligatorios.')
                return redirect('usuarios:crear-usuario')

            # Validar que el email no exista
            if UsuarioCRM.objects.filter(email=email).exists():
                messages.error(request, 'Ya existe un usuario con ese email.')
                return redirect('usuarios:crear-usuario')

            # Crear usuario
            usuario = UsuarioCRM.objects.create_user(
                email=email,
                password=password,
                nombre=nombre,
                rol=rol
            )

            messages.success(request, f'Usuario {nombre} creado exitosamente.')
            return redirect('usuarios:gestion-tramitadores')

        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
            return redirect('usuarios:crear-usuario')


@method_decorator(never_cache, name='dispatch')
class EditarUsuarioView(LoginRequiredMixin, View):
    """
    Vista para editar usuarios existentes.
    """
    def get(self, request, usuario_id):
        if request.user.rol != 'ADMINISTRADOR':
            return redirect('usuarios:login')

        usuario = get_object_or_404(UsuarioCRM, id=usuario_id)

        # No permitir que el admin se edite a sí mismo aquí
        if usuario.id == request.user.id:
            messages.warning(request, 'No puedes editarte a ti mismo desde aquí.')
            return redirect('usuarios:gestion-tramitadores')

        context = {
            'user': request.user,
            'usuario_editar': usuario
        }
        return render(request, 'administrador/editar_usuario.html', context)

    def post(self, request, usuario_id):
        if request.user.rol != 'ADMINISTRADOR':
            return redirect('usuarios:login')

        try:
            usuario = get_object_or_404(UsuarioCRM, id=usuario_id)

            nombre = request.POST.get('nombre')
            email = request.POST.get('email')
            rol = request.POST.get('rol')
            activo = request.POST.get('activo') == 'on'
            password = request.POST.get('password')

            # Validar email único (excepto el actual)
            if UsuarioCRM.objects.filter(email=email).exclude(id=usuario_id).exists():
                messages.error(request, 'Ya existe otro usuario con ese email.')
                return redirect('usuarios:editar-usuario', usuario_id=usuario_id)

            # Actualizar datos
            usuario.nombre = nombre
            usuario.email = email
            usuario.rol = rol
            usuario.is_active = activo

            # Cambiar contraseña solo si se proporciona
            if password and password.strip():
                usuario.set_password(password)

            usuario.save()

            messages.success(request, f'Usuario {nombre} actualizado exitosamente.')
            return redirect('usuarios:gestion-tramitadores')

        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
            return redirect('usuarios:editar-usuario', usuario_id=usuario_id)


@method_decorator(never_cache, name='dispatch')
class EliminarUsuarioView(LoginRequiredMixin, View):
    """
    Vista para eliminar usuarios.
    """
    def post(self, request, usuario_id):
        if request.user.rol != 'ADMINISTRADOR':
            return redirect('usuarios:login')

        try:
            usuario = get_object_or_404(UsuarioCRM, id=usuario_id)

            # No permitir que el admin se elimine a sí mismo
            if usuario.id == request.user.id:
                messages.error(request, 'No puedes eliminarte a ti mismo.')
                return redirect('usuarios:gestion-tramitadores')

            nombre = usuario.nombre
            usuario.delete()

            messages.success(request, f'Usuario {nombre} eliminado exitosamente.')

        except Exception as e:
            messages.error(request, f'Error al eliminar usuario: {str(e)}')

        return redirect('usuarios:gestion-tramitadores')


@method_decorator(never_cache, name='dispatch')
class GestionPlantillasView(LoginRequiredMixin, View):
    """
    Vista para la gestión de plantillas de documentos por parte del administrador.
    Permite subir nuevas plantillas, ver las existentes y eliminarlas.
    """
    def get(self, request):
        if request.user.rol != 'ADMINISTRADOR':
            return redirect('usuarios:login')

        plantillas = get_all_plantillas()
        context = {
            'user': request.user,
            'plantillas': plantillas
        }
        return render(request, 'administrador/gestion_plantillas.html', context)

    def post(self, request):
        if request.user.rol != 'ADMINISTRADOR':
            return redirect('usuarios:login')

        if 'eliminar_plantilla' in request.POST:
            plantilla_id = request.POST.get('plantilla_id')
            try:
                eliminar_plantilla_documento(plantilla_id)
                messages.success(request, 'Plantilla eliminada exitosamente.')
            except PlantillaDocumento.DoesNotExist:
                messages.error(request, 'La plantilla no existe.')
            except Exception as e:
                messages.error(request, f'Error al eliminar plantilla: {str(e)}')
            return redirect('usuarios:gestion-plantillas')

        else: # Lógica para subir una nueva plantilla
            nombre = request.POST.get('nombre')
            segmento = request.POST.get('segmento')
            tipo_especifico = request.POST.get('tipo_especifico')
            archivo = request.FILES.get('archivo_base') # Usar request.FILES para archivos

            try:
                crear_plantilla_documento(nombre, segmento, tipo_especifico, archivo, request.user)
                messages.success(request, 'Plantilla subida exitosamente.')
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Error al subir plantilla: {str(e)}')
            
            return redirect('usuarios:gestion-plantillas')


@method_decorator(never_cache, name='dispatch')
class GestionTramitesAdminView(LoginRequiredMixin, View):
    """
    Vista para que el administrador vea todos los trámites del sistema.
    """
    def get(self, request):
        if request.user.rol != 'ADMINISTRADOR':
            return redirect('usuarios:login')

        tramites = Tramite.objects.select_related(
            'solicitante', 'tramitador_asignado'
        ).order_by('-fecha_inicio')

        context = {
            'user': request.user,
            'tramites': tramites
        }
        return render(request, 'administrador/gestion_tramites.html', context)


@method_decorator(never_cache, name='dispatch')
class DetalleTramiteAdminView(LoginRequiredMixin, View):
    """
    Vista para que el administrador vea el detalle de un trámite específico.
    """
    def get(self, request, tramite_id):
        if request.user.rol != 'ADMINISTRADOR':
            return redirect('usuarios:login')

        tramite = get_object_or_404(
            Tramite.objects.select_related('solicitante', 'tramitador_asignado'),
            id=tramite_id
        )

        # Obtener el último documento
        ultimo_documento = Documento.objects.filter(tramite=tramite).order_by('-version').first()

        # Obtener historial de cambios
        from apps.tramites.models import HistorialCambios
        historial = HistorialCambios.objects.filter(tramite=tramite).order_by('-fecha_cambio')[:10]

        context = {
            'user': request.user,
            'tramite': tramite,
            'documento': ultimo_documento,
            'historial': historial,
        }
        return render(request, 'administrador/detalle_tramite.html', context)


@method_decorator(never_cache, name='dispatch')
class VisualizarPDFAdminView(LoginRequiredMixin, View):
    """
    Vista para que el administrador visualice el PDF de un trámite.
    """
    def get(self, request, tramite_id):
        if request.user.rol != 'ADMINISTRADOR':
            raise Http404("No tiene permiso para ver este documento.")

        tramite = get_object_or_404(Tramite, id=tramite_id)

        # Obtener el documento más reciente
        documento = tramite.documentos.order_by('-version').first()

        if not documento or not documento.archivo:
            raise Http404("No se encontró el documento.")

        try:
            # Retornar el archivo PDF
            return FileResponse(
                documento.archivo.open('rb'),
                content_type='application/pdf',
                as_attachment=False,
                filename=f"{tramite.nombre}_v{documento.version}.pdf"
            )
        except Exception as e:
            raise Http404(f"Error al abrir el documento: {e}")
