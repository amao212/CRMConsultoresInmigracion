from django import forms

class SubirDocumentoForm(forms.Form):
    archivos = forms.FileField(
        label="Seleccionar archivo(s) PDF",
        help_text="Puede seleccionar múltiples archivos. Formato PDF. Tamaño máximo 10MB por archivo.",
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'application/pdf',
            'class': 'form-control-file',
            'multiple': False
        })
    )

    def clean_archivos(self):
        """Validación no se aplica aquí ya que procesamos múltiples archivos en la vista"""
        return self.cleaned_data.get('archivos')
