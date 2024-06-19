from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseForbidden

class AdminAccessMiddleware():
    def __init__(self, get_response):
        self.get_response= get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.is_superuser:
                return HttpResponseForbidden("You don't have permission to access this site")
            
        response = self.get_response(request)
        return response
    
class AdminMiddleware(AdminAccessMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)
