from django.contrib import admin
from shopqna.models import Shopqna

# Register your models here.

class Adminshopqna(admin.ModelAdmin):
    list_display = ("qnanum", "user_id", "qnatitle", "qnacontent", "qnareadcount", "qnaregdate", "repleadmin", "replecontent", "repleregdate")

admin.site.register(Shopqna, Adminshopqna)
