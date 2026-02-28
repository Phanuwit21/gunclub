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
        widgets = {
            "join_date": forms.DateInput(attrs={"type": "date"},format="%Y-%m-%d"),
            "expire_date": forms.DateInput(attrs={"type": "date"},format="%Y-%m-%d"),
        }
        fields = [
            "first_name",
            "last_name",
            "first_name_en",
            "last_name_en",
            "nickname",
            "phone",
            "email",
            "emergency_contact_name",
            "emergency_contact_phone",
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

        # บังคับ format ให้โชว์ถูก
        self.fields["join_date"].input_formats = ["%Y-%m-%d"]
        self.fields["expire_date"].input_formats = ["%Y-%m-%d"]

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
        input_attrs = {
            "class": "w-full border-2 border-slate-300 rounded-lg px-4 py-2.5 "
                     "bg-white text-slate-800 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition"
        }
        for field_name, field in self.fields.items():
            if field_name != "photo":
                if hasattr(field.widget, "attrs"):
                    field.widget.attrs.update(input_attrs)

    def clean_phone(self):
        """แปลงเบอร์โทรให้เป็นตัวเลขเท่านั้น ก่อน validate 9-15 หลัก"""
        value = (self.cleaned_data.get("phone") or "").strip()
        if not value:
            return value
        digits = "".join(c for c in value if c.isdigit())
        if len(digits) < 9 or len(digits) > 15:
            from django.core.exceptions import ValidationError
            raise ValidationError("เบอร์โทรต้องเป็นตัวเลข 9-15 หลักเท่านั้น")
        return digits
