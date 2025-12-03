from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)

class HandleGenericExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            logger.error(f"Erro não tratado: {e}")
            return render(request, 'core/error.html', {'message': "Erro interno no servidor."})
