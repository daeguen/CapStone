from django.contrib import admin
from shopproduct.models import Shopproduct

# Register your models here.
class Adminshopproduct(admin.ModelAdmin):
    list_display = ("prodnum","prodname", "prodprice", "prodquantity", "prodbrand", "proditems" ,"prodmainimg",
                    "prodsubimg1", "prodsubimg2", "prodcontentimg", "prodreadcount", "prodstatus")
    
admin.site.register(Shopproduct, Adminshopproduct)