from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Member


class StaffRegisterForm(UserCreationForm):
    """ฟอร์มสำหรับสร้างบัญชี Staff พร้อม validation ของ Django"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        attrs = {"class": "border border-gray-300 rounded px-3 py-2 w-full"}
        self.fields["username"].widget.attrs.update(attrs)
        self.fields["password1"].widget.attrs.update(attrs)
        self.fields["password2"].widget.attrs.update(attrs)


class MemberForm(forms.ModelForm):

    class Meta:
        model = Member
        fields = [
            "first_name",
            "last_name",
            "first_name_en",
            "last_name_en",
            "nickname",
            "phone",
            "blood_group",
            "address",
            "photo",
            "role",
            "join_date",
            "expire_date",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # default: field ทุกตัวแก้ได้
        role = None
        if user and hasattr(user, "member"):
            role = user.member.role

        # =========================
        # MEMBER (แก้โปรไฟล์ตัวเอง)
        # =========================
        if role == "MEMBER":
            readonly_fields = [
                "role",
                "join_date",
                "expire_date",
            ]
            for field in readonly_fields:
                self.fields.pop(field, None)

        # =========================
        # STAFF / COMMITTEE
        # =========================
        elif role in ["STAFF", "COMMITTEE"]:
            # ห้ามตั้ง role สูงกว่า STAFF
            if "role" in self.fields:
                self.fields["role"].choices = [
                    ("MEMBER", "Member"),
                    ("STAFF", "Staff"),
                ]

        # =========================
        # PRESIDENT
        # =========================
        elif role == "PRESIDENT":
            # เห็นทุก field + ทุก role
            pass

        # สไตล์ input ทุก field
        attrs = {"class": "input-field"}
        for field_name, field in self.fields.items():
            if field_name not in ("photo", "is_active"):
                if hasattr(field.widget, "attrs"):
                    field.widget.attrs.update(attrs)
