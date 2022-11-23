from django.db import models
from shopproduct.models import Shopproduct
from shopmember.models import Shopmember

# Create your models here.
class Shopcart(models.Model):
    cartnum = models.AutoField(verbose_name="카트번호", primary_key=True)
    prodnum = models.ForeignKey(Shopproduct, on_delete=models.CASCADE, db_column="prodnum")
    user_id = models.ForeignKey(Shopmember, on_delete=models.CASCADE, db_column="user_id")
    prodcount = models.IntegerField(verbose_name="개수", default=0)
    prodcolor = models.CharField(verbose_name="상품색상", max_length=100, null=False)
    prodsize = models.CharField(verbose_name="상품사이즈", max_length=100, null=False)
    
class Shopcartpay(models.Model):
    cartpaynum = models.AutoField(verbose_name="주문번호", primary_key=True)
    prodnum = models.ForeignKey(Shopproduct, verbose_name="상품번호", on_delete=models.CASCADE, db_column="prodnum")
    user_id=models.ForeignKey(Shopmember, verbose_name="회원정보", on_delete=models.CASCADE, db_column="user_id")
    prodcount = models.IntegerField(verbose_name="주문개수", null=False)
    prodsize = models.CharField(verbose_name="상품사이즈",max_length=100, null=False)
    prodcolor = models.CharField(verbose_name="상품색깔",max_length=100, null=False)