from django.urls.conf import path
from shopproduct import views

app_name = "product"

urlpatterns = [
    path("prodcontent", views.Prodcontent.as_view(), name="prodcontent"),
    
    path("kang", views.Kangpage.as_view(), name="kang"),
    path("hm", views.Hmpage.as_view(), name="hm"),
    path("northface", views.Northfacepage.as_view(), name="northface"),
    path("spao", views.Spaopage.as_view(), name="spao"),
    
    path("northfacec", views.Nfc.as_view(), name="northfacec"),
    path("kangc", views.Kangc.as_view(), name="kangc"),
    path("hmc", views.Hmc.as_view(), name="hmc"),
    path("spaoc", views.Spaoc.as_view(), name="spaoc"),
    
    
    path("nb", views.Nbpage.as_view(), name="nb"),
    path("muji", views.Mujipage.as_view(), name="muji"),
    path("nike", views.Nikepage.as_view(), name="nike"),
    path("adidas", views.Adpage.as_view(), name="adidas"),
    
    path("nbc", views.Nbc.as_view(), name="nbc"),
    path("mujic", views.Mujic.as_view(), name="mujic"),
    path("nikec", views.Nikec.as_view(), name="nikec"),
    path("adidasc", views.Adc.as_view(), name="adidasc"),  
    ]
