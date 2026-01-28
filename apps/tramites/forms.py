from django import forms
from django.core.exceptions import ValidationError

class SubirDocumentoForm(forms.Form):
    archivo = forms.FileField(
        label="Seleccionar archivo PDF",
        help_text="Formato PDF. Tamaño máximo 10MB.",
        widget=forms.ClearableFileInput(attrs={'accept': 'application/pdf', 'class': 'form-control-file'})
    )

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            if archivo.content_type != 'application/pdf':
                raise ValidationError("El archivo debe ser un PDF.")
            if archivo.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError("El archivo no debe superar los 10MB.")
        return archivo
