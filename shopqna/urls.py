from django.urls.conf import path
from shopqna import views

app_name="qnaboard"

urlpatterns = [
    path("qnalist", views.Qnalist.as_view(), name="qnalist"),
    path("qnawrtie", views.Qnawrite.as_view(), name="qnawrite"),
    path("qnacontent", views.Qnacontent.as_view(), name="qnacontent"),
    path("qnadelete", views.Qnadelete.as_view(), name="qnadelete"),
    path("qnamodify", views.Qnamodify.as_view(), name="qnamodify"),
    path("qnamodifypro", views.Qnamodifypro.as_view(), name="qnamodifypro"),
    path("myqna", views.Myqna.as_view(), name="myqna"),
    ]