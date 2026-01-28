import io
import os
from datetime import timedelta
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.db import transaction
import PyPDF2
from apps.tramites.models import Tramite, Documento, PlantillaDocumento
from .tramite_data_service import TramiteDataService
from .asignacion_service import AsignacionTramitadorService
from .storage_service import _generar_ruta_archivo


def _rellenar_pdf_plantilla(plantilla: PlantillaDocumento, form_data: dict) -> io.BytesIO:
    """
    Rellena el PDF original de la plantilla con los datos del formulario.
    Inyecta los valores directamente en los campos del PDF usando PyPDF2.
    """
    try:
        # Abrir el PDF de la plantilla
        pdf_path = plantilla.archivo_base.path

        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            pdf_writer = PyPDF2.PdfWriter()

            # Verificar si el PDF tiene campos de formulario
            if '/AcroForm' in pdf_reader.trailer['/Root']:
                print(f"✅ PDF tiene campos de formulario. Rellenando...")

                # Copiar todas las páginas
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)

                # Limpiar datos: remover csrfmiddlewaretoken y convertir todos a string
                datos_limpios = {}
                for key, value in form_data.items():
                    if key != 'csrfmiddlewaretoken':
                        datos_limpios[key] = str(value) if value else ''

                print(f"📝 Rellenando {len(datos_limpios)} campos...")

                # Rellenar los campos usando el método correcto de PyPDF2 3.x
                try:
                    # Método para PyPDF2 3.x - actualizar campos por página
                    if hasattr(pdf_writer, 'update_page_form_field_values'):
                        pdf_writer.update_page_form_field_values(
                            pdf_writer.pages[0],
                            datos_limpios
                        )
                        print(f"✅ Campos rellenados usando update_page_form_field_values")
                    else:
                        # Método alternativo: manipular directamente las anotaciones
                        page = pdf_writer.pages[0]
                        if '/Annots' in page:
                            annotations = page['/Annots']
                            for annotation in annotations:
                                annotation_obj = annotation.get_object()
                                if annotation_obj.get('/T'):  # Campo tiene nombre
                                    field_name = annotation_obj.get('/T')
                                    if field_name in datos_limpios:
                                        # Actualizar el valor del campo
                                        annotation_obj.update({
                                            PyPDF2.generic.NameObject('/V'): PyPDF2.generic.TextStringObject(datos_limpios[field_name])
                                        })
                        print(f"✅ Campos rellenados usando manipulación directa de anotaciones")

                except Exception as e_fill:
                    print(f"⚠️ Error al rellenar campos: {e_fill}")
                    print("📝 Intentando método de superposición...")
                    return _generar_pdf_con_datos_superpuestos(plantilla, form_data, pdf_reader)

                # NO aplanar para que se puedan ver los datos
                # if hasattr(pdf_writer, 'flatten'):
                #     pdf_writer.flatten()
            else:
                print(f"⚠️ El PDF no tiene campos de formulario")
                # Usar el método de texto superpuesto
                return _generar_pdf_con_datos_superpuestos(plantilla, form_data, pdf_reader)

            # Guardar el PDF rellenado en memoria
            buffer = io.BytesIO()
            pdf_writer.write(buffer)
            buffer.seek(0)
            print(f"✅ PDF generado exitosamente")
            return buffer

    except Exception as e:
        print(f"❌ Error al rellenar el PDF: {e}")
        import traceback
        traceback.print_exc()
        # Si falla, intentar con el método alternativo
        return _generar_pdf_con_datos_superpuestos(plantilla, form_data)


def _generar_pdf_con_datos_superpuestos(plantilla: PlantillaDocumento, form_data: dict, pdf_reader=None) -> io.BytesIO:
    """
    Método alternativo: Superpone los datos sobre el PDF original.
    Se usa cuando el PDF no tiene campos de formulario o falla el método de inyección.
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from PyPDF2 import PdfWriter, PdfReader

    try:
        if pdf_reader is None:
            pdf_path = plantilla.archivo_base.path
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)

        # Crear un PDF con los datos en reportlab
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # Posicionar los datos en el PDF
        # Esto es un ejemplo básico - necesitarás ajustar las coordenadas
        y_position = 700
        x_position = 100

        for key, value in form_data.items():
            if key != 'csrfmiddlewaretoken':
                campo_legible = key.replace('_', ' ').title()
                can.drawString(x_position, y_position, f"{campo_legible}: {value}")
                y_position -= 20
                if y_position < 100:
                    can.showPage()
                    y_position = 700

        can.save()
        packet.seek(0)

        # Crear un nuevo PDF que combine la plantilla con los datos
        overlay_pdf = PdfReader(packet)
        output = PdfWriter()

        # Agregar todas las páginas de la plantilla
        for i, page in enumerate(pdf_reader.pages):
            if i == 0 and len(overlay_pdf.pages) > 0:
                # Superponer los datos en la primera página
                page.merge_page(overlay_pdf.pages[0])
            output.add_page(page)

        # Guardar el resultado
        buffer = io.BytesIO()
        output.write(buffer)
        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"Error al superponer datos en el PDF: {e}")
        # Último recurso: crear un PDF simple con los datos
        return _generar_pdf_simple_fallback(plantilla, form_data)


def _generar_pdf_simple_fallback(plantilla: PlantillaDocumento, form_data: dict) -> io.BytesIO:
    """
    Último recurso: Genera un PDF simple con los datos del formulario.
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título del documento
    p.drawString(72, height - 72, f"Datos para Trámite: {plantilla.nombre}")
    p.line(72, height - 80, width - 72, height - 80)

    # Escribir los datos del formulario
    y_position = height - 120
    for key, value in form_data.items():
        if key not in ['csrfmiddlewaretoken']:
            campo_legible = key.replace('_', ' ').capitalize()
            p.drawString(72, y_position, f"{campo_legible}: {value}")
            y_position -= 20
            if y_position < 50:
                p.showPage()
                y_position = height - 72

    p.save()
    buffer.seek(0)
    return buffer

def iniciar_nuevo_tramite(solicitante, plantilla: PlantillaDocumento, form_data: dict):
    """
    Orquesta la creación de un nuevo trámite, su documento PDF inicial y las entradas en la BD.
    ASIGNA AUTOMÁTICAMENTE un tramitador disponible al trámite.

    Estructura de carpetas:
    media/solicitante/solicitante_0001/[segmento]/[tipo_tramite]_v1.pdf

    El PDF se genera rellenando la plantilla original con los datos del formulario.

    Args:
        solicitante: Usuario solicitante (propietario del trámite)
        plantilla: PlantillaDocumento a usar
        form_data: Datos del formulario enviados por el usuario

    Returns:
        Tramite creado
    """
    # 1. Validar y limpiar datos del formulario
    # Si form_data está vacío (flujo de subida de PDF), no validamos campos requeridos
    if form_data:
        datos_limpios = TramiteDataService.validar_datos_formulario(form_data, plantilla)
    else:
        datos_limpios = {}

    # 2. Crear el Trámite en la base de datos con los datos validados
    fecha_limite = timezone.now() + timedelta(days=90)  # Fecha límite por defecto de 90 días
    tramite = Tramite.objects.create(
        solicitante=solicitante,
        nombre=plantilla.tipo_especifico,  # El nombre del trámite es el tipo de la plantilla
        estado='PENDIENTE',  # Estado inicial: Pendiente de aprobación
        fecha_limite=fecha_limite,
        datos_formulario=datos_limpios  # Guardar los datos validados en el campo JSON
    )
    
    # Asignar la plantilla al trámite (temporalmente como atributo para _generar_ruta_archivo)
    tramite.plantilla = plantilla

    print(f"✅ Trámite #{tramite.id} creado para solicitante #{solicitante.id}")
    print(f"📋 Datos guardados: {len(datos_limpios)} campos")

    # 3. ASIGNAR TRAMITADOR AUTOMÁTICAMENTE (NUEVO)
    asignado = AsignacionTramitadorService.asignar_tramitador_a_tramite(tramite)
    if asignado:
        print(f"👤 Tramitador asignado: {tramite.tramitador_asignado.email}")
    else:
        print("⚠️ No se pudo asignar tramitador (no hay tramitadores disponibles)")

    # 4. Rellenar el PDF de la plantilla con los datos del formulario
    pdf_buffer = _rellenar_pdf_plantilla(plantilla, datos_limpios)

    # 5. Definir el nombre base del archivo
    tipo_limpio = plantilla.tipo_especifico.lower().replace(' ', '_')
    nombre_base = f"{tipo_limpio}.pdf"

    # 6. Crear el objeto Documento y guardar el archivo
    # Usamos transacción para asegurar consistencia en la versión
    with transaction.atomic():
        # Bloquear registros para evitar condiciones de carrera en la versión
        # Aunque es el primer documento, es buena práctica si hubiera reintentos rápidos
        last_doc = Documento.objects.select_for_update().filter(
            tramite=tramite, 
            nombre=plantilla.tipo_especifico
        ).order_by('-version').first()
        
        version_actual = (last_doc.version + 1) if last_doc else 1

        # Verificar existencia física para evitar colisiones y sufijos aleatorios
        while True:
            ruta_archivo = _generar_ruta_archivo(tramite, plantilla.tipo_especifico, version_actual, nombre_base)
            if not default_storage.exists(ruta_archivo):
                break
            version_actual += 1

        documento = Documento(
            tramite=tramite,
            nombre=plantilla.tipo_especifico,  # El nombre del documento es el tipo de trámite
            version=version_actual
        )
        
        # Envolvemos el PDF en memoria para que Django lo pueda guardar
        archivo_django = SimpleUploadedFile(nombre_base, pdf_buffer.read(), content_type='application/pdf')
        
        # Guardar usando la ruta explícita para evitar hash aleatorio
        # NOTA: Al usar upload_to dinámico en el modelo, save() usará esa función.
        # Pero si pasamos el nombre aquí, Django podría usarlo.
        # Sin embargo, el modelo Documento ahora tiene upload_to=documento_upload_to.
        # Si pasamos solo el archivo, Django usará la función del modelo.
        # Pero aquí queremos forzar el nombre que ya calculamos para asegurar consistencia.
        # La función del modelo recalculará lo mismo.
        
        # Para evitar duplicidad de lógica, confiamos en el modelo, pero le pasamos el nombre correcto al archivo
        archivo_django.name = os.path.basename(ruta_archivo)
        documento.archivo = archivo_django
        documento.save()

    print(f"📄 Documento generado: {ruta_archivo}")

    return tramite


def actualizar_datos_tramite(tramite_id: int, solicitante, form_data: dict):
    """
    Actualiza los datos de un trámite existente y regenera el PDF.
    Solo el solicitante propietario puede actualizar sus trámites.

    Args:
        tramite_id: ID del trámite a actualizar
        solicitante: Usuario solicitante (debe ser el propietario)
        form_data: Nuevos datos del formulario

    Returns:
        Tramite actualizado

    Raises:
        PermissionDenied: Si el usuario no es el propietario
        ValidationError: Si los datos no son válidos
    """
    # 1. Guardar datos de forma segura (valida propiedad automáticamente)
    tramite = TramiteDataService.guardar_datos_formulario(tramite_id, solicitante, form_data)

    print(f"✅ Trámite #{tramite.id} actualizado para solicitante #{solicitante.id}")
    print(f"📋 Datos actualizados: {len(tramite.datos_formulario)} campos")

    # 2. Obtener la plantilla asociada
    plantilla = PlantillaDocumento.objects.get(tipo_especifico=tramite.nombre, activo=True)
    tramite.plantilla = plantilla # Asignar para _generar_ruta_archivo

    # 3. Regenerar el PDF con los nuevos datos
    pdf_buffer = _rellenar_pdf_plantilla(plantilla, tramite.datos_formulario)

    # 4. Crear nueva versión del documento de forma segura
    with transaction.atomic():
        # Bloquear para obtener la última versión real y evitar condiciones de carrera
        ultimo_documento = Documento.objects.select_for_update().filter(
            tramite=tramite,
            nombre=plantilla.tipo_especifico
        ).order_by('-version').first()
        
        nueva_version = (ultimo_documento.version + 1) if ultimo_documento else 1

        # 5. Definir el nombre base del archivo
        tipo_limpio = plantilla.tipo_especifico.lower().replace(' ', '_')
        nombre_base = f"{tipo_limpio}.pdf"
        
        # Verificar existencia física para evitar colisiones y sufijos aleatorios
        while True:
            ruta_archivo = _generar_ruta_archivo(tramite, plantilla.tipo_especifico, nueva_version, nombre_base)
            if not default_storage.exists(ruta_archivo):
                break
            nueva_version += 1

        # 6. Crear el nuevo documento con la nueva versión
        documento = Documento(
            tramite=tramite,
            nombre=plantilla.tipo_especifico,
            version=nueva_version
        )

        archivo_django = SimpleUploadedFile(nombre_base, pdf_buffer.read(), content_type='application/pdf')
        
        # Para evitar duplicidad de lógica, confiamos en el modelo, pero le pasamos el nombre correcto al archivo
        archivo_django.name = os.path.basename(ruta_archivo)
        documento.archivo = archivo_django
        documento.save()

    print(f"📄 Documento actualizado: {ruta_archivo}")

    return tramite


def generar_pdf_desde_tramite(tramite_id: int, solicitante_id: int) -> io.BytesIO:
    """
    Genera un PDF a partir de un trámite existente de forma segura.
    Valida que el solicitante sea el propietario del trámite.

    Args:
        tramite_id: ID del trámite
        solicitante_id: ID del solicitante (para validación de seguridad)

    Returns:
        Buffer con el PDF generado

    Raises:
        ValidationError: Si el trámite no existe o no pertenece al solicitante
    """
    # Obtener el trámite con validación de propiedad
    tramite = TramiteDataService.obtener_tramite_con_datos(tramite_id, solicitante_id)

    # Obtener la plantilla asociada
    plantilla = PlantillaDocumento.objects.get(tipo_especifico=tramite.nombre, activo=True)

    # Generar el PDF con los datos guardados
    pdf_buffer = _rellenar_pdf_plantilla(plantilla, tramite.datos_formulario)

    return pdf_buffer
