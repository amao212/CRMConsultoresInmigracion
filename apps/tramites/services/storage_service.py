import os
from django.core.files.storage import default_storage
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
    solicitante_id = tramite.solicitante.id
    documento_nombre_clean = nombre_documento.lower().replace(' ', '_')
    
    # Obtener extensión
    _, ext = os.path.splitext(filename)
    
    # Construir nombre: nombre_vX.ext
    new_filename = f"{documento_nombre_clean}_v{version}{ext}"
    
    # Segmento
    segmento = 'general'
    if hasattr(tramite, 'plantilla') and tramite.plantilla:
        segmento = tramite.plantilla.segmento.lower().replace(' ', '_')
    elif hasattr(tramite, 'nombre'):
         segmento = tramite.nombre.split()[0].lower()

    return f"solicitante_{solicitante_id}/{segmento}/{new_filename}"

def guardar_documento(tramite, archivo_subido):
    # Clasificar
    nombre_base = os.path.splitext(archivo_subido.name)[0]
    nombre_documento = clasificar_documento(archivo_subido.name)
    if nombre_documento == 'Documento':
         nombre_documento = nombre_base
    
    # Determinar versión inicial basada en DB
    last_doc = Documento.objects.filter(tramite=tramite, nombre=nombre_documento).order_by('-version').first()
    version_actual = (last_doc.version + 1) if last_doc else 1
    
    # Verificar existencia en storage para evitar colisiones y nombres aleatorios
    # Si el archivo existe (por ejemplo, archivos huérfanos sin registro en DB), incrementamos la versión
    while True:
        file_path = _generar_ruta_archivo(tramite, nombre_documento, version_actual, archivo_subido.name)
        if not default_storage.exists(file_path):
            break
        version_actual += 1
        
    # Crear objeto
    doc = Documento(tramite=tramite, nombre=nombre_documento, version=version_actual)
    
    # Guardar archivo en la ruta específica
    # Al pasar el path explícito a save(), Django usará ese nombre exacto.
    # Como ya verificamos que no existe, no debería agregar caracteres aleatorios.
    doc.archivo.save(file_path, archivo_subido)
    
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
