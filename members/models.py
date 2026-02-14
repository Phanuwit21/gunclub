from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import uuid


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

    phone = models.CharField(max_length=20, blank=True)

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

    # -----------------------
    # LOGIC
    # -----------------------

    def save(self, *args, **kwargs):
        if not self.member_id:
            last_member = Member.objects.order_by('id').last()
            if last_member:
                last_number = int(last_member.member_id.split('-')[1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.member_id = f"GC-{new_number:03d}"

        if not self.expire_date:
            self.expire_date = self.join_date + timedelta(days=365)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member_id} - {self.first_name} {self.last_name}"

    @property
    def status(self):
        if self.expire_date >= date.today():
            return "Active"
        return "Expired"

    def get_card_url(self):
        from django.conf import settings
        base = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
        return f"{base}/member/{self.public_id}/"


    def is_expired(self):
        return self.expire_date < timezone.now().date()

    def is_expiring_soon(self, days=30):
        today = timezone.now().date()
        return today <= self.expire_date <= today + timedelta(days=days)