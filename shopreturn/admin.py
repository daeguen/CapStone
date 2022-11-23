from django.contrib import admin
from shopreturn.models import Prodreturn


# Register your models here.
class ProdreturnAdmin(admin.ModelAdmin):
    list_display =("returnnum","prodnum","prodname","user_id",
                   "return_title","return_content","return_img","return_status",
                   "return_message","return_msg_regdate","return_regdate")
    
admin.site.register(Prodreturn,ProdreturnAdmin)