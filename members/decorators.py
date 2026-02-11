from django.shortcuts import redirect
from django.contrib import messages
from .models import Member

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            member = Member.objects.get(user=request.user)

            if member.role not in allowed_roles:
                messages.error(request, "คุณไม่มีสิทธิ์เข้าหน้านี้")
                return redirect("member_profile")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
