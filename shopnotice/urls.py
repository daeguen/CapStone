from django.urls.conf import path
from shopnotice import views

app_name="notice"
urlpatterns = [
    path("noticelist", views.Noticelist.as_view(), name="noticelist"),
    path("noticedetail", views.Noticedetail.as_view(), name="noticedetail"),
    
    ]