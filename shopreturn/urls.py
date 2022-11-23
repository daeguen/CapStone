from django.urls.conf import path
from shopreturn import views

app_name="return"
urlpatterns = [
        path("returnlist",views.Returnlist.as_view(),name="returnlist"),
        path("returncontent",views.Returncontent.as_view(), name="returncontent"),
        path("returndelete",views.Returndelete.as_view(), name="returndelete"),
        path("returnmodify",views.Returnmodify.as_view(), name="returnmodify"),
        path("returnmodifypro",views.Returnmodifypro.as_view(), name="returnmodifypro"),
        path("returnwrite", views.Returnwrite.as_view(), name="returnwrite"),   
        ]