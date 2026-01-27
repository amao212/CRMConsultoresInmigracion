from django.urls import path
from .views_roles.login_view import LoginView, LogoutView
from .views_roles.admin_view import (
    AdminDashboardView,
    GestionEmpleadosView,
    CrearUsuarioView,
    EditarUsuarioView,
    EliminarUsuarioView,
    GestionPlantillasView  # Importar la nueva vista
)
from .views_roles.empleado_view import EmpleadoDashboardView
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
    path('dashboard-empleado/', EmpleadoDashboardView.as_view(), name='dashboard-empleado'),
    path('dashboard-solicitante/', SolicitanteDashboardView.as_view(), name='dashboard-solicitante'),

    # --- Gestión de Administrador ---
    path('gestion-empleados/', GestionEmpleadosView.as_view(), name='gestion-empleados'),
    path('crear-usuario/', CrearUsuarioView.as_view(), name='crear-usuario'),
    path('editar-usuario/<int:usuario_id>/', EditarUsuarioView.as_view(), name='editar-usuario'),
    path('eliminar-usuario/<int:usuario_id>/', EliminarUsuarioView.as_view(), name='eliminar-usuario'),
    path('gestion-plantillas/', GestionPlantillasView.as_view(), name='gestion-plantillas'), # Nueva ruta
]
