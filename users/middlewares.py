from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.urls import reverse

class GroupMiddlewareAccess():
    def __init__(self, get_response, group_name):
        self.get_response= get_response
        self.group_name= group_name

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.is_superuser:
                if not request.user.groups.filter(name= self.group_name).exists():
                    return HttpResponseForbidden("You don't have the permission to access this site")
        
        response= self.get_response(request)
        return response
    
class EditorsMiddleware(GroupMiddlewareAccess):
    def __init__(self, get_response):
        super().__init__(get_response, group_name='Editors')