import os
from django.db import transaction
from apps.tramites.models import Documento, HistorialCambios, PlantillaDocumento
from .pdf_field_extractor import extraer_campos_pdf

# --- Funciones para Documentos de Solicitantes ---

def clasificar_documento(nombre_archivo):
    nombre_lower = nombre_archivo.lower()
    if 'pasaporte' in nombre_lower:
        return 'Pasaporte'
    elif 'visa' in nombre_lower:
        return 'Visa'
    return 'Documento'

def _generar_ruta_archivo(tramite, nombre_documento, version, filename):
    """
    Genera la ruta de archivo para un documento. Esta función debe ser consistente
    con documento_upload_to en models.py
    """
    solicitante_id = tramite.solicitante.id

    # Normalizar nombre del documento para el archivo (slug)
    documento_nombre_clean = nombre_documento.lower().replace(' ', '_')

    # Obtener extensión
    _, ext = os.path.splitext(filename)

    # Construir nombre: nombre_vX.ext
    new_filename = f"{documento_nombre_clean}_v{version}{ext}"

    # Segmento
    segmento = 'general'

    # Intentar obtener la plantilla para determinar el segmento correcto
    plantilla = getattr(tramite, 'plantilla', None)
    if not plantilla and hasattr(tramite, 'nombre'):
        try:
            plantilla = PlantillaDocumento.objects.filter(tipo_especifico=tramite.nombre).first()
        except Exception:
            pass

    if plantilla:
        segmento = plantilla.segmento.lower().replace(' ', '_')
    elif hasattr(tramite, 'nombre'):
         segmento = tramite.nombre.split()[0].lower()

    return f"solicitante/solicitante_{solicitante_id:04d}/{segmento}/{new_filename}"

def guardar_documento(tramite, archivo_subido):
    # Usar el nombre del trámite como tipo de documento base
    # Esto asegura que el archivo se llame como el trámite (ej: visa_trabajo_v1.pdf)
    nombre_documento = tramite.nombre
    
    # Usamos una transacción atómica para evitar condiciones de carrera al calcular la versión
    with transaction.atomic():
        # Bloquear los registros de documentos de este trámite para lectura/escritura
        # Esto asegura que si dos procesos intentan subir un archivo al mismo tiempo, uno espere al otro
        # y la versión se calcule correctamente.
        last_doc = Documento.objects.select_for_update().filter(
            tramite=tramite, 
            nombre=nombre_documento
        ).order_by('-version').first()
        
        version_actual = (last_doc.version + 1) if last_doc else 1
        
        # Crear objeto Documento con la versión calculada
        # El modelo usará automáticamente documento_upload_to para generar la ruta correcta
        doc = Documento(
            tramite=tramite,
            nombre=nombre_documento,
            version=version_actual,
            archivo=archivo_subido
        )

        # Guardar el documento - Django creará automáticamente las carpetas necesarias
        doc.save()
    
    HistorialCambios.objects.create(
        tramite=tramite,
        descripcion=f"Se subió el documento '{nombre_documento}' (versión {version_actual})."
    )
    return doc

# --- Funciones para Plantillas de Documentos (Admin) ---

def crear_plantilla_documento(nombre, segmento, tipo_especifico, archivo, administrador):
    """
    Crea una nueva plantilla de documento en la base de datos y extrae automáticamente
    los campos del PDF.
    """
    if not all([nombre, segmento, tipo_especifico, archivo, administrador]):
        raise ValueError("Todos los campos son requeridos para crear la plantilla.")

    plantilla = PlantillaDocumento.objects.create(
        nombre=nombre,
        segmento=segmento,
        tipo_especifico=tipo_especifico,
        archivo_base=archivo,
        administrador=administrador
    )

    # Extraer campos automáticamente del PDF
    try:
        campos_creados = extraer_campos_pdf(plantilla)
        print(f"✅ Se crearon {campos_creados} campos automáticamente para la plantilla '{nombre}'")
    except Exception as e:
        print(f"⚠️ No se pudieron extraer campos automáticamente: {e}")

    return plantilla

def eliminar_plantilla_documento(plantilla_id: int):
    """
    Elimina una plantilla de documento por su ID.
    """
    plantilla = PlantillaDocumento.objects.get(id=plantilla_id)
    if plantilla.archivo_base:
        plantilla.archivo_base.delete(save=False)
    plantilla.delete()
