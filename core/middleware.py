class NoCacheMiddleware:
    """
    Middleware para deshabilitar el caché del navegador en vistas protegidas.
    Esto previene que los usuarios puedan ver páginas anteriores usando el botón 'Atrás'
    después de cerrar sesión.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si el usuario está autenticado, forzamos a que el navegador no guarde caché
        if hasattr(request, 'user') and request.user.is_authenticated:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
        return response
