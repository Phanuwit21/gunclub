from django import forms
from .models import Member

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
