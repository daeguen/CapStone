from django.urls.conf import path
from shopmember import views

app_name="member"

urlpatterns = [
        path("index", views.Index.as_view(), name="index"),
        path("signup", views.MemberSignup.as_view(), name="signup"),
        path("login", views.MemberLogin.as_view(), name="login"),
        path("confirm", views.MemberConfirm.as_view(),name="confirm"),
        path("logout", views.MemberLogout.as_view(),name="logout"),
        path("delete", views.MemberDelete.as_view(),name="delete"),
        path("modify", views.MemberModify.as_view(),name="modify"),
        path("modifypro", views.MemberModifypro.as_view(),name="modifypro"),
        path("mypage", views.Membermypage.as_view(),name="mypage"),     
        path("pappap", views.Fitpapup.as_view(),name="pappap"),
        path("myreview", views.Myreview.as_view(), name="myreview"),
    ] 