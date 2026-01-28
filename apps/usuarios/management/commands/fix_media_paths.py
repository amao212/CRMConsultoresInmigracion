import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.tramites.models import Documento, PlantillaDocumento

class Command(BaseCommand):
    help = 'Corrige las rutas de los archivos en media/ para seguir el patrón solicitante/solicitante_<id>/'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando migración de rutas de archivos...")
        
        media_root = settings.MEDIA_ROOT
        documentos = Documento.objects.select_related('tramite', 'tramite__solicitante').all()
        
        count_migrated = 0
        count_errors = 0
        count_skipped = 0
        
        for doc in documentos:
            try:
                old_path = doc.archivo.name
                if not old_path:
                    continue
                    
                # Verificar si ya tiene el formato correcto
                solicitante_id = doc.tramite.solicitante.id
                # Usamos 4 dígitos para el ID (ej: 0006) para mantener orden
                expected_prefix = f"solicitante/solicitante_{solicitante_id:04d}/"
                
                if old_path.startswith(expected_prefix):
                    count_skipped += 1
                    continue
                
                # Construir nueva ruta
                # Extraer nombre de archivo
                filename = os.path.basename(old_path)
                
                # Determinar segmento de forma robusta
                segmento = 'general'
                try:
                    # Intentar buscar la plantilla asociada al trámite por nombre
                    plantilla = PlantillaDocumento.objects.filter(tipo_especifico=doc.tramite.nombre).first()
                    if plantilla:
                        segmento = plantilla.segmento.lower().replace(' ', '_')
                    elif hasattr(doc.tramite, 'nombre'):
                         segmento = doc.tramite.nombre.split()[0].lower()
                except Exception:
                    # Fallback si falla la consulta
                    if hasattr(doc.tramite, 'nombre'):
                         segmento = doc.tramite.nombre.split()[0].lower()
                
                new_relative_path = f"{expected_prefix}{segmento}/{filename}"
                
                # Rutas absolutas en el sistema de archivos
                abs_old_path = os.path.join(media_root, old_path)
                abs_new_path = os.path.join(media_root, new_relative_path)
                
                # Verificar si el archivo original existe
                if not os.path.exists(abs_old_path):
                    # Si no existe en la ruta vieja, verificamos si ya está en la nueva (por si se corrió parcialmente)
                    if os.path.exists(abs_new_path):
                        self.stdout.write(self.style.WARNING(f"Archivo ya estaba en destino pero DB desactualizada: {new_relative_path}"))
                        doc.archivo.name = new_relative_path
                        doc.save()
                        count_migrated += 1
                        continue
                    else:
                        self.stdout.write(self.style.WARNING(f"Archivo no encontrado en disco (omitido): {abs_old_path}"))
                        count_errors += 1
                        continue
                
                # Crear directorios si no existen
                os.makedirs(os.path.dirname(abs_new_path), exist_ok=True)
                
                # Mover archivo
                shutil.move(abs_old_path, abs_new_path)
                
                # Actualizar base de datos
                doc.archivo.name = new_relative_path
                doc.save()
                
                self.stdout.write(self.style.SUCCESS(f"Migrado: {old_path} -> {new_relative_path}"))
                count_migrated += 1
                
                # Intentar limpiar directorios vacíos antiguos
                # Esto ayuda a mantener limpia la carpeta media
                try:
                    old_dir = os.path.dirname(abs_old_path)
                    if os.path.exists(old_dir) and not os.listdir(old_dir):
                        os.rmdir(old_dir)
                        # Intentar subir un nivel más si es solicitante_X (formato antiguo)
                        parent_dir = os.path.dirname(old_dir)
                        parent_name = os.path.basename(parent_dir)
                        if parent_name.startswith('solicitante_') and not os.listdir(parent_dir):
                             os.rmdir(parent_dir)
                except OSError:
                    pass # Directorio no vacío o error de permisos, ignorar
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error migrando documento {doc.id}: {e}"))
                count_errors += 1
        
        self.stdout.write(self.style.SUCCESS(f"Proceso finalizado.\nMigrados: {count_migrated}\nOmitidos (ya correctos): {count_skipped}\nErrores/No encontrados: {count_errors}"))
