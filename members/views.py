from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from .decorators import role_required
from .forms import MemberForm, StaffRegisterForm
from .models import Member
from django.utils import timezone


# =========================
# AUTH
# =========================

def staff_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            try:
                member = Member.objects.get(user=user)

                if member.role in ["STAFF", "COMMITTEE", "PRESIDENT"]:
                    return redirect("staff_dashboard")
                else:
                    return redirect("member_dashboard")

            except Member.DoesNotExist:
                return redirect("staff_dashboard")

        return render(request, "members/staff_login.html", {
            "error": "Invalid login"
        })

    return render(request, "members/staff_login.html")


def staff_logout(request):
    logout(request)
    return redirect("staff_login")


# =========================
# STAFF DASHBOARD
# =========================

@login_required
@role_required(["STAFF", "COMMITTEE", "PRESIDENT"])
def staff_dashboard(request):
    today = date.today()

    total = Member.objects.count()
    active = Member.objects.filter(expire_date__gte=today).count()
    expired = Member.objects.filter(expire_date__lt=today).count()

    expiring_soon = Member.objects.filter(
        expire_date__gte=today,
        expire_date__lte=today + timedelta(days=30)
    ).order_by("expire_date")[:5]

    expired_members = Member.objects.filter(
        expire_date__lt=today
    ).order_by("-expire_date")[:5]

    new_members = Member.objects.order_by("-join_date")[:5]

    return render(request, "members/staff_dashboard.html", {
        "total": total,
        "active": active,
        "expired": expired,
        "expiring_soon": expiring_soon,
        "expired_members": expired_members,
        "new_members": new_members,
    })


@login_required
@role_required(["PRESIDENT", "COMMITTEE"])
def staff_register(request):
    if request.method == "POST":
        form = StaffRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # สร้าง Member profile ให้ Staff (จำเป็นสำหรับ role_required)
            Member.objects.create(
                user=user,
                first_name=user.username,
                last_name="Staff",
                join_date=date.today(),
                role="STAFF",
            )
            messages.success(request, f"สร้างบัญชี Staff '{user.username}' เรียบร้อยแล้ว")
            return redirect("staff_dashboard")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = StaffRegisterForm()

    return render(request, "members/staff_register.html", {"form": form})


# =========================
# MEMBER MANAGEMENT
# =========================

@login_required
@role_required(["STAFF", "COMMITTEE", "PRESIDENT"])
def member_list(request):
    query = request.GET.get("q")

    if query:
        members_qs = Member.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(member_id__icontains=query) |
            Q(nickname__icontains=query)
        ).order_by("-id")
    else:
        members_qs = Member.objects.all().order_by("-id")

    paginator = Paginator(members_qs, 15)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    new_member_credentials = None
    if "new_member_credentials" in request.session:
        new_member_credentials = request.session.pop("new_member_credentials")

    return render(request, "members/member_list.html", {
        "members": page_obj,
        "page_obj": page_obj,
        "new_member_credentials": new_member_credentials,
    })


@login_required
@role_required(["STAFF", "COMMITTEE", "PRESIDENT"])
def add_member(request):
    if request.method == "POST":
        form = MemberForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            member = form.save(commit=False)

            random_password = User.objects.make_random_password(length=12)

            user = User.objects.create_user(
                username="temp_user",
                password=random_password
            )

            member.user = user
            member.save()

            user.username = member.member_id
            user.save()

            request.session["new_member_credentials"] = {
                "username": member.member_id,
                "password": random_password,
            }

            return redirect("member_list")
    else:
        form = MemberForm(user=request.user)

    return render(request, "members/add_member.html", {"form": form})



@login_required
@role_required(["STAFF", "COMMITTEE", "PRESIDENT"])
def edit_member(request, pk):
    member = get_object_or_404(Member, pk=pk)

    if request.method == "POST":
        form = MemberForm(request.POST, request.FILES, instance=member, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"แก้ไขข้อมูล {member.member_id} เรียบร้อยแล้ว")
            return redirect("member_list")
    else:
        form = MemberForm(instance=member, user=request.user)

    return render(request, "members/edit_member.html", {
        "form": form,
        "member": member
    })



@login_required
@role_required(["STAFF", "COMMITTEE", "PRESIDENT"])
def delete_member(request, member_id):
    member = get_object_or_404(Member, member_id=member_id)

    if request.method == "POST":
        if member.user:
            member.user.delete()

        member.delete()
        messages.success(request, f"ลบสมาชิก {member.member_id} เรียบร้อยแล้ว")
        return redirect("member_list")

    return render(request, "members/delete_member.html", {"member": member})


# =========================
# MEMBER AREA
# =========================

@login_required
def member_dashboard(request):
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        messages.error(request, "ไม่มีข้อมูลสมาชิก")
        return redirect("staff_login")

    return render(request, "members/member_dashboard.html", {
        "member": member
    })


@login_required
def edit_profile(request):
    member = request.user.member
    role = member.role

    if request.method == "POST":
        form = MemberForm(
            request.POST,
            request.FILES,
            instance=member,
            user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "บันทึกโปรไฟล์เรียบร้อยแล้ว")

            # redirect ตาม role
            if role == "MEMBER":
                return redirect("member_dashboard")
            else:
                return redirect("staff_dashboard")
    else:
        form = MemberForm(
            instance=member,
            user=request.user
        )

    # เลือก template ตาม role
    if role == "MEMBER":
        template_name = "members/edit_profile_member.html"
    else:
        template_name = "members/edit_profile_staff.html"

    return render(request, template_name, {
        "form": form,
        "member": member
    })




@login_required
def change_password(request):
    member = request.user.member
    is_staff_side = member.role in ["STAFF", "COMMITTEE", "PRESIDENT"]

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "เปลี่ยนรหัสผ่านเรียบร้อยแล้ว")

            if is_staff_side:
                return redirect("staff_dashboard")
            return redirect("member_dashboard")
    else:
        form = PasswordChangeForm(request.user)

    template = (
        "members/change_password_staff.html"
        if is_staff_side
        else "members/change_password_member.html"
    )

    return render(request, template, {"form": form})


# =========================
# PUBLIC CARD
# =========================

def member_card(request, public_id):
    member = get_object_or_404(Member, public_id=public_id)

    # เช็กวันหมดอายุ
    if member.expire_date and member.expire_date < timezone.now().date():
        return redirect('member_card_expired', public_id=member.public_id)

    return render(request, 'members/member_card.html', {
        'member': member,
        "today": date.today()
    })

def member_card_expired(request, public_id):
    member = get_object_or_404(Member, public_id=public_id)

    return render(request, 'members/member_card_expired.html', {
        'member': member,
        "today": date.today()
    })



@login_required
def my_card(request):
    member = get_object_or_404(Member, user=request.user)
    return redirect("member_card", public_id=member.public_id)


# =========================
# MEMBER DETAIL
# =========================

@login_required
@role_required(["STAFF", "COMMITTEE", "PRESIDENT"])
def member_detail(request, member_id):
    member = get_object_or_404(Member, member_id=member_id)
    return render(request, "members/member_detail.html", {"member": member})


