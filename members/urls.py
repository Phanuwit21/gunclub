from django.urls import path
from . import views

urlpatterns = [

    # staff
    path("login/", views.staff_login, name="staff_login"),
    path("logout/", views.staff_logout, name="staff_logout"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/register/", views.staff_register, name="staff_register"),

    # member management
    path("members/", views.member_list, name="member_list"),
    path("members/add/", views.add_member, name="add_member"),

    # profile
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    # public card
    path("member/<uuid:public_id>/", views.member_card, name="member_card"),
    path("member/<uuid:public_id>/expired/", views.member_card_expired, name="member_card_expired"),
    path("member/<uuid:public_id>/print/", views.card_print, name="card_print"),
    path("card/<uuid:public_id>/", views.member_card_view_only, name="member_card_view_only"),
    path("card/<uuid:public_id>/expired/", views.member_card_expired_view_only, name="member_card_expired_view_only"),
    path("my-card/", views.my_card, name="my_card"),
    path("dashboard/", views.member_dashboard, name="member_dashboard"),


    # edit/delete
    path("edit/<int:pk>/", views.edit_member, name="edit_member"),
    path("delete/<str:member_id>/", views.delete_member, name="delete_member"),
    path("password/", views.change_password, name="change_password"),


    # MUST BE LAST
    path("<str:member_id>/", views.member_detail, name="member_detail"),
]
