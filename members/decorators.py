from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import Member

def role_required(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            try:
                member = Member.objects.get(user=request.user)
            except Member.DoesNotExist:
                messages.error(request, _("คุณไม่มีสิทธิ์เข้าหน้านี้"))
                return redirect("staff_login")

            if member.role not in allowed_roles:
                messages.error(request, _("คุณไม่มีสิทธิ์เข้าหน้านี้"))
                if member.role == "MEMBER":
                    return redirect("member_dashboard")
                return redirect("staff_dashboard")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
