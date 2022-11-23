from django.contrib import admin
from shopnotice.models import Shopnotice

# Register your models here.
class AdminShopnotice(admin.ModelAdmin):
    list_display = ("noticenum","adminname", "noticetitle", "noticecontent", "noticereadcount", "noticeregdate")

admin.site.register(Shopnotice, AdminShopnotice)
