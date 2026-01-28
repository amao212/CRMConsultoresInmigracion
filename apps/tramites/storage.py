"""
Storage personalizado que no agrega sufijos aleatorios a los archivos.
En su lugar, sobrescribe archivos existentes.
"""
from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    """
    Storage que sobrescribe archivos existentes en lugar de agregar sufijos aleatorios.
    """
    def get_available_name(self, name, max_length=None):
        """
        Retorna el nombre del archivo sin agregar sufijos aleatorios.
        Si el archivo existe, será sobrescrito.
        """
        # Eliminar el archivo existente si existe
        if self.exists(name):
            self.delete(name)
        return name
