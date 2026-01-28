import os
import django
from django.conf import settings
from django.test.runner import DiscoverRunner
from django.db import transaction

def before_all(context):
    """
    Configura el entorno de Django antes de ejecutar cualquier prueba.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    
    # Configurar entorno de pruebas de Django
    # interactive=False evita que pregunte si borrar la BD existente
    context.test_runner = DiscoverRunner(interactive=False)
    context.test_runner.setup_test_environment()
    context.old_db_config = context.test_runner.setup_databases()

def after_all(context):
    """
    Limpieza después de todas las pruebas.
    """
    context.test_runner.teardown_databases(context.old_db_config)
    context.test_runner.teardown_test_environment()

def before_scenario(context, scenario):
    """
    Se ejecuta antes de cada escenario.
    Inicia una transacción atómica para aislar los cambios del escenario.
    """
    # Iniciar transacción atómica usando la API correcta de Django
    context.scenario_transaction = transaction.atomic()
    context.scenario_transaction.__enter__()

def after_scenario(context, scenario):
    """
    Se ejecuta después de cada escenario.
    Hace rollback de la transacción para limpiar la base de datos.
    """
    # Rollback de la transacción para revertir cambios
    # transaction.atomic() hace rollback automático si sale con excepción,
    # pero aquí forzamos el rollback al salir del contexto manualmente si es necesario,
    # o simplemente cerramos el bloque.
    # Para simular el comportamiento de TestCase, necesitamos revertir todo.
    transaction.set_rollback(True)
    context.scenario_transaction.__exit__(None, None, None)
