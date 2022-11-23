from django.contrib import admin
from shopreview.models import Shopreview

# Register your models here.
class Reviewadmin(admin.ModelAdmin):
    list_display = ("prodnum", "user_id", "reviewnum", "reviewtitle", "reviewcontent", "reviewimg", "reviewrating", "reviewregdate")

admin.site.register(Shopreview, Reviewadmin)