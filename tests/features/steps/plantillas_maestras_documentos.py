from behave import *
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta
import os

use_step_matcher("re")

@step(r"que existe un usuario solicitante autenticado en el sistema")
def step_impl_usuario_autenticado(context):
    """
    Crea un usuario solicitante de prueba y lo autentica (simulado).
    """
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    
    # Limpiar usuario previo si existe
    Usuario.objects.filter(email='solicitante.plantillas@example.com').delete()
    
    context.usuario = Usuario.objects.create_user(
        email='solicitante.plantillas@example.com',
        password='password123',
        nombre='Solicitante Plantillas',
        rol='SOLICITANTE'
    )

@step(r'que existe una plantilla maestra activa configurada para el trámite "Visa de Turismo"')
def step_impl_plantilla_maestra(context):
    """
    Crea una plantilla maestra de documento basada en la tabla del feature.
    """
    from apps.tramites.models import PlantillaDocumento
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    
    # Crear admin dummy para la plantilla
    admin, _ = Usuario.objects.get_or_create(
        email='admin.plantillas@example.com',
        defaults={'nombre': 'Admin Plantillas', 'rol': 'ADMINISTRADOR', 'is_staff': True}
    )
    
    # Limpiar plantillas previas
    PlantillaDocumento.objects.all().delete()
    
    for row in context.table:
        nombre = row['nombre_plantilla']
        segmento = row['segmento']
        archivo_nombre = row['archivo_base']
        
        # Crear archivo dummy
        archivo_dummy = SimpleUploadedFile(archivo_nombre, b"contenido_dummy_pdf", content_type="application/pdf")
        
        context.plantilla_maestra = PlantillaDocumento.objects.create(
            nombre=nombre,
            segmento=segmento,
            tipo_especifico="Visa de Turismo", # Mapeo directo al tipo de trámite
            archivo_base=archivo_dummy,
            administrador=admin,
            activo=True
        )

@step(r'que el solicitante inicia un nuevo trámite de tipo "Visa de Turismo"')
def step_impl_inicia_tramite(context):
    """
    Crea un nuevo trámite para el solicitante.
    """
    from apps.tramites.models import Tramite
    
    # Limpiar trámites previos
    Tramite.objects.all().delete()
    
    context.tramite = Tramite.objects.create(
        solicitante=context.usuario,
        nombre="Visa de Turismo",
        fecha_limite=timezone.now() + timedelta(days=90),
        estado='PENDIENTE'
    )

@step(r"el solicitante solicita descargar la plantilla asociada al trámite")
def step_impl_descarga_plantilla(context):
    """
    Simula la descarga de la plantilla.
    """
    from apps.tramites.models import PlantillaDocumento
    
    # Buscar la plantilla asociada al trámite
    plantilla = PlantillaDocumento.objects.get(tipo_especifico=context.tramite.nombre, activo=True)
    
    # Simular descarga obteniendo el archivo
    context.archivo_descargado = plantilla.archivo_base

@step(r"el sistema debe permitir descargar la plantilla asociada")
def step_impl_permitir_descarga(context):
    """
    Verifica que se haya obtenido un archivo.
    """
    assert context.archivo_descargado is not None, "No se entregó ningún archivo"

@step(r"el archivo descargado debe ser un PDF")
def step_impl_verificar_pdf(context):
    """
    Verifica que el archivo descargado sea un PDF (por extensión).
    """
    nombre_archivo = context.archivo_descargado.name
    assert nombre_archivo.lower().endswith('.pdf'), f"El archivo {nombre_archivo} no parece ser un PDF"

@step(r'que el solicitante tiene un trámite activo de tipo "Visa de Turismo"')
def step_impl_tramite_activo(context):
    """
    Asegura que existe un trámite activo. Reutiliza la lógica de creación.
    """
    # Si ya existe en el contexto, lo usamos, si no, lo creamos
    if not hasattr(context, 'tramite'):
        from apps.tramites.models import Tramite
        
        # Limpiar trámites previos
        Tramite.objects.all().delete()
        
        context.tramite = Tramite.objects.create(
            solicitante=context.usuario,
            nombre="Visa de Turismo",
            fecha_limite=timezone.now() + timedelta(days=90),
            estado='PENDIENTE'
        )
        
        # Asegurar que existe la plantilla para que funcione la lógica de nombres
        from apps.tramites.models import PlantillaDocumento
        if not PlantillaDocumento.objects.filter(tipo_especifico="Visa de Turismo").exists():
             # Crear plantilla dummy si no existe (para que el upload_to funcione)
             from django.contrib.auth import get_user_model
             Usuario = get_user_model()
             admin = Usuario.objects.filter(rol='ADMINISTRADOR').first()
             if not admin:
                 admin = Usuario.objects.create(email='admin.dummy@test.com', rol='ADMINISTRADOR')
                 
             archivo_dummy = SimpleUploadedFile("plantilla_base.pdf", b"dummy", content_type="application/pdf")
             PlantillaDocumento.objects.create(
                nombre="Plantilla Dummy",
                segmento="Visas",
                tipo_especifico="Visa de Turismo",
                archivo_base=archivo_dummy,
                administrador=admin,
                activo=True
            )

@step(r"el solicitante sube un archivo PDF completado para este trámite")
def step_impl_sube_pdf(context):
    """
    Simula la subida de un documento (primera versión).
    """
    from apps.tramites.models import Documento
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    # Simular archivo subido
    archivo_subido = SimpleUploadedFile("formulario_completado.pdf", b"contenido_pdf_v1", content_type="application/pdf")
    
    documento = Documento(
        tramite=context.tramite,
        nombre="Visa de Turismo", # El nombre del documento suele ser el tipo de trámite
        version=1,
        archivo=archivo_subido
    )
    documento.save()
    context.documento_subido = documento

@step(r"el sistema debe guardar el documento exitosamente")
def step_impl_verifica_guardado(context):
    """
    Verifica que el documento se haya guardado en la BD.
    """
    assert context.documento_subido.pk is not None, "El documento no se guardó en la base de datos"

@step(r"debe registrarse un documento asociado al trámite")
def step_impl_verificar_asociacion(context):
    """
    Verifica que el documento esté asociado al trámite correcto.
    """
    assert context.documento_subido.tramite == context.tramite, "El documento no está asociado al trámite correcto"

@step(r"la versión registrada debe ser (?P<version>\d+)")
def step_impl_verificar_version(context, version):
    """
    Verifica el número de versión del documento.
    """
    version_esperada = int(version)
    assert context.documento_subido.version == version_esperada, \
        f"La versión del documento es {context.documento_subido.version}, se esperaba {version_esperada}"

@step(r"que ya existe un documento cargado previamente para este trámite con versión 1")
def step_impl_existe_documento_previo(context):
    """
    Crea un documento previo para probar el versionado.
    """
    from apps.tramites.models import Documento
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    archivo_v1 = SimpleUploadedFile("previo.pdf", b"contenido_v1", content_type="application/pdf")
    
    doc_v1 = Documento.objects.create(
        tramite=context.tramite,
        nombre="Visa de Turismo",
        version=1,
        archivo=archivo_v1
    )
    context.documento_previo = doc_v1

@step(r"el solicitante sube un nuevo archivo PDF corregido para el mismo trámite")
def step_impl_sube_correccion(context):
    """
    Simula la subida de una segunda versión del documento.
    """
    from apps.tramites.models import Documento
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    archivo_v2 = SimpleUploadedFile("corregido.pdf", b"contenido_v2", content_type="application/pdf")
    
    # Lógica de versionado (normalmente en vista/servicio, aquí simulada en step)
    ultima_version = Documento.objects.filter(
        tramite=context.tramite, 
        nombre="Visa de Turismo"
    ).order_by('-version').first().version
    
    nueva_version = ultima_version + 1
    
    documento_v2 = Documento(
        tramite=context.tramite,
        nombre="Visa de Turismo",
        version=nueva_version,
        archivo=archivo_v2
    )
    documento_v2.save()
    context.documento_subido = documento_v2

@step(r"el sistema debe guardar el nuevo documento como una nueva versión")
def step_impl_verifica_nueva_version_guardada(context):
    """
    Verifica que se haya creado un nuevo registro de documento y que sea distinto al anterior.
    """
    assert context.documento_subido.pk is not None
    if hasattr(context, 'documento_previo'):
        assert context.documento_subido.pk != context.documento_previo.pk, "No se creó un nuevo registro para la nueva versión"

@step(r"la versión registrada debe incrementarse a (?P<version>\d+)")
def step_impl_verificar_incremento(context, version):
    """
    Verifica que la versión se haya incrementado al valor esperado.
    """
    version_esperada = int(version)
    assert context.documento_subido.version == version_esperada, \
        f"La versión no se incrementó correctamente. Esperada: {version_esperada}, Actual: {context.documento_subido.version}"


@step("el solicitante sube dos archivos PDF completados para este trámite")
def step_impl_sube_dos_pdfs(context):
    from apps.tramites.models import Documento
    from django.core.files.uploadedfile import SimpleUploadedFile
    # Simular primer archivo subido
    archivo_subido_1 = SimpleUploadedFile("formulario_completado_1.pdf", b"contenido_pdf_v1", content_type="application/pdf")
    documento_1 = Documento(
        tramite=context.tramite,
        nombre="Visa de Turismo",
        version=1,
        archivo=archivo_subido_1
    )
    documento_1.save()

    # Simular segundo archivo subido
    archivo_subido_2 = SimpleUploadedFile("formulario_completado_2.pdf", b"contenido_pdf_v2", content_type="application/pdf")
    documento_2 = Documento(
        tramite=context.tramite,
        nombre="Visa de Turismo",
        version=2,
        archivo=archivo_subido_2
    )
    documento_2.save()
    context.documentos_subidos = [documento_1, documento_2]


@step("el sistema debe guardar los documentos exitosamente")
def step_impl_verifica_guardado_multiple(context):
    assert hasattr(context, 'documentos_subidos'), "No se encontraron documentos subidos en el contexto"
    assert len(context.documentos_subidos) == 2, f"Se esperaban 2 documentos, se encontraron {len(context.documentos_subidos)}"
    for documento in context.documentos_subidos:
        assert documento.pk is not None, f"El documento {documento.nombre} versión {documento.version} no se guardó en la base de datos"


@step("debe registrarse dos documentos asociados al trámite")
def step_impl_verificar_dos_documentos_asociados(context):
    assert hasattr(context, 'documentos_subidos'), "No se encontraron documentos subidos en el contexto"
    assert len(context.documentos_subidos) == 2, f"Se esperaban 2 documentos, se encontraron {len(context.documentos_subidos)}"
    for documento in context.documentos_subidos:
        assert documento.tramite == context.tramite, \
            f"El documento versión {documento.version} no está asociado al trámite correcto"
