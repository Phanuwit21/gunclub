from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
from datetime import timedelta
import uuid

# เบอร์โทรต้องเป็นตัวเลข 9-15 หลัก (รองรับไทยและต่างประเทศ)
phone_validator = RegexValidator(
    regex=r'^[0-9]{9,15}$',
    message='เบอร์โทรต้องเป็นตัวเลข 9-15 หลักเท่านั้น',
)


class Member(models.Model):

    ROLE_CHOICES = [
        ('MEMBER', 'Member'),
        ('STAFF', 'Staff'),
        ('COMMITTEE', 'Committee'),
        ('PRESIDENT', 'President'),
    ]

    BLOOD_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    member_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # -----------------------
    # NAME
    # -----------------------

    # Thai name
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # English name
    first_name_en = models.CharField(max_length=100, blank=True)
    last_name_en = models.CharField(max_length=100, blank=True)

    nickname = models.CharField(max_length=50, blank=True)

    # -----------------------
    # PERSONAL INFO
    # -----------------------

    phone = models.CharField(max_length=20, blank=True, validators=[phone_validator])

    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_CHOICES,
        blank=True
    )

    address = models.TextField(blank=True)

    photo = models.ImageField(upload_to='member_photos/', blank=True, null=True)

    # -----------------------
    # MEMBERSHIP
    # -----------------------

    join_date = models.DateField()
    expire_date = models.DateField(blank=True, null=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='MEMBER'
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['public_id']),
            models.Index(fields=['member_id']),
        ]

    # -----------------------
    # LOGIC
    # -----------------------

    def save(self, *args, **kwargs):
        if not self.expire_date and self.join_date:
            self.expire_date = self.join_date + timedelta(days=365)

        if not self.member_id:
            with transaction.atomic():
                last_member = Member.objects.select_for_update().order_by('-id').first()
                if last_member:
                    last_number = int(last_member.member_id.split('-')[1])
                    new_number = last_number + 1
                else:
                    new_number = 1
                self.member_id = f"GC-{new_number:03d}"
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member_id} - {self.first_name} {self.last_name}"

    @property
    def status(self):
        if self.expire_date and self.expire_date >= timezone.now().date():
            return "Active"
        return "Expired"

    # def get_card_url(self):
    #     """URL สำหรับดูบัตร (มีปุ่มกลับ สำหรับสมาชิกที่ล็อกอิน)"""
    #     from django.conf import settings
    #     base = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    #     return f"{base}/member/{self.public_id}/"

    def get_card_view_only_url(self):
        """URL สำหรับ QR scan - แสดงเฉพาะบัตร ไม่มีปุ่มกลับ ป้องกันผู้สแกนเข้าถึงระบบ"""
        from django.conf import settings
        base = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
        return f"{base}/card/{self.public_id}/"


    def is_expired(self):
        if self.expire_date is None:
            return True
        return self.expire_date < timezone.now().date()

    def is_valid(self):
        """บัตรใช้งานได้ เมื่อ is_active=True และ expire_date >= วันนี้"""
        if not self.is_active:
            return False
        if not self.expire_date:
            return False
        if self.expire_date < timezone.now().date():
            return False
        return True

    def is_expiring_soon(self, days=30):
        if self.expire_date is None:
            return False
        today = timezone.now().date()
        return today <= self.expire_date <= today + timedelta(days=days)