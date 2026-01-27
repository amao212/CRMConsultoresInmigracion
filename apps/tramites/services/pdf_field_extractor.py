"""
Servicio para extraer campos de formularios PDF automáticamente
"""
import PyPDF2
from django.core.files.storage import default_storage
from apps.tramites.models import CampoPlantilla
import os
import re


def extraer_campos_pdf(plantilla):
    """
    Extrae los campos de un formulario PDF y crea objetos CampoPlantilla automáticamente.

    Args:
        plantilla: Instancia de PlantillaDocumento

    Returns:
        int: Número de campos creados
    """
    if not plantilla.archivo_base:
        return 0

    # Obtener la ruta del archivo
    pdf_path = plantilla.archivo_base.path

    try:
        # Abrir el PDF
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Verificar si el PDF tiene campos de formulario
            if '/AcroForm' not in pdf_reader.trailer['/Root']:
                print(f"⚠️ El PDF '{plantilla.nombre}' no tiene campos de formulario.")
                return crear_campos_genericos(plantilla)

            # Obtener los campos del formulario
            fields = pdf_reader.get_form_text_fields()

            if not fields:
                print(f"⚠️ No se encontraron campos en el PDF '{plantilla.nombre}'.")
                return crear_campos_genericos(plantilla)

            # Eliminar campos existentes para evitar duplicados
            plantilla.campos.all().delete()

            campos_creados = 0
            orden = 1

            for field_name, field_value in fields.items():
                # Limpiar el nombre del campo para mostrarlo al usuario
                nombre_campo = limpiar_nombre_campo(field_name)
                # IMPORTANTE: Usar el nombre REAL del campo PDF como nombre_tecnico
                # Esto permite que el rellenado funcione correctamente
                nombre_tecnico = field_name  # Mantener el nombre original del PDF
                tipo_campo = detectar_tipo_campo(field_name)

                # Crear el campo
                CampoPlantilla.objects.create(
                    plantilla=plantilla,
                    nombre_campo=nombre_campo,
                    nombre_tecnico=nombre_tecnico,  # Nombre real del campo en el PDF
                    tipo_campo=tipo_campo,
                    es_requerido=True,
                    orden=orden
                )

                campos_creados += 1
                orden += 1

                print(f"  ✅ Campo extraído: {nombre_campo} -> {nombre_tecnico} ({tipo_campo})")

            return campos_creados

    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo PDF en {pdf_path}")
        return crear_campos_genericos(plantilla)
    except Exception as e:
        print(f"❌ Error al extraer campos del PDF: {e}")
        return crear_campos_genericos(plantilla)


def crear_campos_genericos(plantilla):
    """
    Crea campos genéricos basados en el tipo de trámite cuando no se pueden extraer del PDF.
    """
    print(f"📝 Creando campos genéricos para '{plantilla.nombre}'...")

    # Eliminar campos existentes
    plantilla.campos.all().delete()

    # Definir campos genéricos comunes para cualquier trámite
    campos_genericos = [
        {
            'nombre_campo': 'Nombre Completo',
            'nombre_tecnico': 'nombre_completo',
            'tipo_campo': 'text',
            'es_requerido': True,
            'orden': 1
        },
        {
            'nombre_campo': 'Número de Identificación/Pasaporte',
            'nombre_tecnico': 'numero_identificacion',
            'tipo_campo': 'text',
            'es_requerido': True,
            'orden': 2
        },
        {
            'nombre_campo': 'Fecha de Nacimiento',
            'nombre_tecnico': 'fecha_nacimiento',
            'tipo_campo': 'date',
            'es_requerido': True,
            'orden': 3
        },
        {
            'nombre_campo': 'Correo Electrónico',
            'nombre_tecnico': 'email',
            'tipo_campo': 'email',
            'es_requerido': True,
            'orden': 4
        },
        {
            'nombre_campo': 'Número de Teléfono',
            'nombre_tecnico': 'telefono',
            'tipo_campo': 'text',
            'es_requerido': True,
            'orden': 5
        },
        {
            'nombre_campo': 'Dirección Completa',
            'nombre_tecnico': 'direccion',
            'tipo_campo': 'textarea',
            'es_requerido': True,
            'orden': 6
        },
        {
            'nombre_campo': 'Nacionalidad',
            'nombre_tecnico': 'nacionalidad',
            'tipo_campo': 'text',
            'es_requerido': True,
            'orden': 7
        },
    ]

    # Agregar campos específicos según el segmento o tipo
    if 'visa' in plantilla.nombre.lower() or 'visa' in plantilla.segmento.lower():
        campos_genericos.extend([
            {
                'nombre_campo': 'Tipo de Visa Solicitada',
                'nombre_tecnico': 'tipo_visa',
                'tipo_campo': 'text',
                'es_requerido': True,
                'orden': 8
            },
            {
                'nombre_campo': 'Propósito del Viaje',
                'nombre_tecnico': 'proposito_viaje',
                'tipo_campo': 'textarea',
                'es_requerido': True,
                'orden': 9
            },
        ])

    if 'trabajo' in plantilla.nombre.lower() or 'trabajo' in plantilla.tipo_especifico.lower():
        campos_genericos.extend([
            {
                'nombre_campo': 'Empresa Empleadora',
                'nombre_tecnico': 'empresa_empleadora',
                'tipo_campo': 'text',
                'es_requerido': True,
                'orden': 10
            },
            {
                'nombre_campo': 'Cargo a Desempeñar',
                'nombre_tecnico': 'cargo',
                'tipo_campo': 'text',
                'es_requerido': True,
                'orden': 11
            },
        ])

    # Siempre agregar campo de aceptación
    campos_genericos.append({
        'nombre_campo': 'Acepto términos y condiciones',
        'nombre_tecnico': 'acepta_terminos',
        'tipo_campo': 'checkbox',
        'es_requerido': True,
        'orden': 99
    })

    # Crear los campos
    for campo_data in campos_genericos:
        CampoPlantilla.objects.create(
            plantilla=plantilla,
            **campo_data
        )

    return len(campos_genericos)


def limpiar_nombre_campo(nombre):
    """
    Convierte el nombre técnico del campo PDF en un nombre legible.
    Ejemplos:
        'nombre_completo' -> 'Nombre Completo'
        'fecha_nacimiento' -> 'Fecha de Nacimiento'
        'PASSPORT_NUMBER' -> 'Passport Number'
    """
    # Reemplazar guiones bajos y guiones por espacios
    nombre = nombre.replace('_', ' ').replace('-', ' ')

    # Capitalizar cada palabra
    nombre = nombre.title()

    # Reemplazar abreviaturas comunes
    reemplazos = {
        'Id': 'ID',
        'Dni': 'DNI',
        'Nro': 'Número',
        'Tel': 'Teléfono',
        'Dir': 'Dirección',
    }

    for old, new in reemplazos.items():
        nombre = nombre.replace(old, new)

    return nombre


def crear_nombre_tecnico(nombre):
    """
    Convierte un nombre de campo en un nombre técnico válido.
    Ejemplos:
        'Nombre Completo' -> 'nombre_completo'
        'Fecha de Nacimiento' -> 'fecha_nacimiento'
        'E-mail Address' -> 'email_address'
    """
    # Convertir a minúsculas
    nombre = nombre.lower()

    # Reemplazar caracteres especiales y espacios por guiones bajos
    nombre = re.sub(r'[^\w\s]', '', nombre)
    nombre = re.sub(r'\s+', '_', nombre)

    return nombre


def detectar_tipo_campo(nombre_campo):
    """
    Detecta el tipo de campo basándose en el nombre.
    """
    nombre_lower = nombre_campo.lower()

    # Detectar email
    if 'email' in nombre_lower or 'correo' in nombre_lower or 'mail' in nombre_lower:
        return 'email'

    # Detectar fecha
    if 'fecha' in nombre_lower or 'date' in nombre_lower or 'birth' in nombre_lower or 'nacimiento' in nombre_lower:
        return 'date'

    # Detectar número
    if 'numero' in nombre_lower or 'number' in nombre_lower or 'cantidad' in nombre_lower or 'phone' in nombre_lower or 'telefono' in nombre_lower:
        return 'number'

    # Detectar checkbox
    if 'acepto' in nombre_lower or 'acepta' in nombre_lower or 'agree' in nombre_lower or 'check' in nombre_lower or 'terminos' in nombre_lower:
        return 'checkbox'

    # Detectar textarea (campos largos)
    if 'descripcion' in nombre_lower or 'description' in nombre_lower or 'comentario' in nombre_lower or 'comment' in nombre_lower or 'direccion' in nombre_lower or 'address' in nombre_lower or 'proposito' in nombre_lower or 'purpose' in nombre_lower:
        return 'textarea'

    # Por defecto, texto corto
    return 'text'
