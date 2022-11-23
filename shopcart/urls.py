from django.urls.conf import path
from shopcart import views

app_name="prodcart"
urlpatterns = [
    path("prodcart", views.Prodcart.as_view(), name="prodcart"),
    path("cartdelete", views.Cartdelete.as_view(), name="cartdelete"),
    path("basecartdelete", views.Baseartdelete.as_view(), name="basecartdelete"),
    path("cartupdate", views.Cartupdate.as_view(), name="cartupdate"),
    path("cartpaydetail", views.Cartpaydetail.as_view(), name="cartpaydetail"),
    path("cartpaydelete", views.Cartpaydelete.as_view(), name="cartpaydelete"),
    path("cartpaydeleteall", views.Cartpaydeleteall.as_view(), name="cartpaydeleteall"),
    ]