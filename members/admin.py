from django.contrib import admin
from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'member_id',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'expire_date',
    )
    search_field = ('member_id', 'first_name', 'last_name')
    list_filter = ('role', 'is_active')