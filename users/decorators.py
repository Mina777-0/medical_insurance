from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden

def group_required(group_name):
    def in_group(user):
        if user.is_authenticated:
            if user.groups.filter(name= group_name).exists() or user.is_superuser:
                return True
        return False
    return user_passes_test(in_group)

