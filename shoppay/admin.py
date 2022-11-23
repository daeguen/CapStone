from django.contrib import admin
from shoppay.models import Shoppay, Shoppaydetail, Paydata

# Register your models here.
class Shoppayadmin(admin.ModelAdmin):
    list_display = ("paynum", "prodnum", "user_id", "prodcount", "prodsize", "prodcolor")

admin.site.register(Shoppay, Shoppayadmin)

class Shoppaydetailadmin(admin.ModelAdmin):
    list_display=("paydetailnum", "user_id", "prodnum",
                  "user_name", "user_tel", "addressee","addressee_tel", "user_addr", "user_addrt",
                  "prodmainimg","prodname", "prodprice","prodcount", "prodoption", "total_pay",
                  "paytype", "paycommant", "common_door", "delively_status", "payreg_date")
    
admin.site.register(Shoppaydetail, Shoppaydetailadmin)

class Paydataadmin(admin.ModelAdmin):
    list_display = ("paynum", "prodnum", "user_id", "prodcount", "prodsize", "prodcolor")

admin.site.register(Paydata, Paydataadmin)