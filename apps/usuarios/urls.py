from django.urls import path
from .views_roles.login_view import LoginView, LogoutView
from .views_roles.admin_view import (
    AdminDashboardView,
    GestionTramitadoresView,
    CrearUsuarioView,
    EditarUsuarioView,
    EliminarUsuarioView,
    GestionPlantillasView,
    GestionTramitesAdminView,
    DetalleTramiteAdminView,
    VisualizarPDFAdminView
)
from .views_roles.tramitador_view import TramitadorDashboardView
from .views_roles.registro_view import RegistroView
from .views_roles.solicitante_view import SolicitanteDashboardView

app_name = 'usuarios'

urlpatterns = [
    # --- Autenticación y Registro ---
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registro/', RegistroView.as_view(), name='registro'),

    # --- Dashboards por Rol ---
    path('dashboard-admin/', AdminDashboardView.as_view(), name='dashboard-admin'),
    path('dashboard-tramitador/', TramitadorDashboardView.as_view(), name='dashboard-tramitador'),
    path('dashboard-solicitante/', SolicitanteDashboardView.as_view(), name='dashboard-solicitante'),

    # --- Gestión de Administrador ---
    path('gestion-tramitadores/', GestionTramitadoresView.as_view(), name='gestion-tramitadores'),
    path('crear-usuario/', CrearUsuarioView.as_view(), name='crear-usuario'),
    path('editar-usuario/<int:usuario_id>/', EditarUsuarioView.as_view(), name='editar-usuario'),
    path('eliminar-usuario/<int:usuario_id>/', EliminarUsuarioView.as_view(), name='eliminar-usuario'),
    path('gestion-plantillas/', GestionPlantillasView.as_view(), name='gestion-plantillas'),
    path('gestion-tramites/', GestionTramitesAdminView.as_view(), name='gestion-tramites'),
    path('tramite/<int:tramite_id>/', DetalleTramiteAdminView.as_view(), name='detalle-tramite-admin'),
    path('tramite/<int:tramite_id>/pdf/', VisualizarPDFAdminView.as_view(), name='visualizar-pdf-admin'),
]
