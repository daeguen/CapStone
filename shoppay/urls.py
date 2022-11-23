from django.urls.conf import path
from shoppay import views

app_name="pay"

urlpatterns = [
    path("payment", views.Payment.as_view(), name="payment"),
    path("paydelete", views.Paydelete.as_view(), name="paydelete"),
    path("ordermodify", views.Ordermodify.as_view(), name="ordermodify"),
    path("ordermodifypro", views.Ordermodifypro.as_view(), name="ordermodifypro"),
    path("ordercancel",views.Ordercancel.as_view(), name="ordercancel"),
    path("ordercomplite",views.Ordercomplite.as_view(), name="ordercomplite"),
    ]