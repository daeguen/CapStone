from django.contrib import admin
from shopmember.models import Shopmember, Shopmemberdelete, Shoprecome

# Register your models here.
class AdminShopmember(admin.ModelAdmin):
    list_display = ("user_id", "user_passwd", "user_name", "user_tel", "user_email", "user_addr", "user_addrt", "user_gender", "user_brand")

admin.site.register(Shopmember, AdminShopmember)

class AdminShopmemberdelete(admin.ModelAdmin):
    list_display = ("user_id", "user_passwd", "user_name", "user_tel", "user_addr", "user_addrt", "user_gender", "user_brand")

admin.site.register(Shopmemberdelete, AdminShopmemberdelete)

class AdminShoprecome(admin.ModelAdmin):
    list_display = ("id", "prodnum")

admin.site.register(Shoprecome, AdminShoprecome)