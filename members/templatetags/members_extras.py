from django import template

register = template.Library()


@register.filter
def can_register_staff(user):
    """ตรวจว่า user มีสิทธิ์สร้าง Staff หรือไม่ (COMMITTEE, PRESIDENT)"""
    try:
        return user.member.role in ("COMMITTEE", "PRESIDENT")
    except Exception:
        return False
