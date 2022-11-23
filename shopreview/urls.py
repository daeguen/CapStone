from django.urls.conf import path
from shopreview import views

app_name="shopreview"

urlpatterns = [
    path("shopreview", views.Review.as_view(), name="shopreview"),
    path("shopreviewmodify", views.Reviewmodify.as_view(), name="shopreviewmodify"),
    path("shopreviewmodifypro", views.Reviewmodifypro.as_view(), name="shopreviewmodifypro"),
    path("shopreviewdelete", views.Reviewdelete.as_view(), name="shopreviewdelete"),
    ]