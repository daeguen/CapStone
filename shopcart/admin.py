from django.contrib import admin
from shopcart.models import Shopcart, Shopcartpay

# Register your models here.
class Shopcartadmin(admin.ModelAdmin):
    list_display = ("cartnum", "prodnum", "user_id", "prodcolor", "prodsize", "prodcount")

admin.site.register(Shopcart, Shopcartadmin)

class Shopcartpayadmin(admin.ModelAdmin):
    list_display = ("cartpaynum", "prodnum", "user_id", "prodcount", "prodsize", "prodcolor")

admin.site.register(Shopcartpay, Shopcartpayadmin)