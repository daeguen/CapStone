from django.db import models
from shopreturn.choices import RETURN_CHOICE
from shoppay.models import Shoppaydetail

# Create your models here.
class Prodreturn(models.Model):
    returnnum = models.AutoField(verbose_name="반품번호",primary_key=True)              #반품번호
    paydetailnum = models.ForeignKey(Shoppaydetail, verbose_name="주문번호", on_delete=models.CASCADE, db_column="paydetailnum", null=False)                 #주문번호
    prodnum = models.IntegerField(verbose_name= "상품번호",null=False)                  #상품번호
    prodname = models.CharField(max_length=200,verbose_name="상품이름",null=False)      #상품이름
    user_id = models.CharField(max_length=30, verbose_name="아이디",null=False)        #유저 아이디
    return_title = models.CharField(max_length=300,verbose_name="반품제목",null=False)  #반품제목
    return_content = models.TextField( verbose_name="반품내용",null=False)              #반품 내용
    return_img = models.ImageField( upload_to = "반품사진", null=False)                 #반품사진
    return_status = models.CharField( choices= RETURN_CHOICE,max_length=100, verbose_name="반품승인상태", null = False, default="진행중") #반품승인상태 (진행중 /  승인 /  불가 )
    returnadmin = models.CharField(max_length=50, verbose_name="반품답변작성자", null=True) #반품답변관리자
    return_message = models.CharField(max_length=4000,verbose_name="반품불가 사유")       #반품불가 사유
    return_msg_regdate= models.DateTimeField(auto_now_add=True, verbose_name="관리자메세지 작성일")#반품사유 작성일
    return_regdate = models.DateTimeField(auto_now_add=True, verbose_name="반품작성일", blank=True) #반품작성일(user)