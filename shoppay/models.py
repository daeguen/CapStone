from django.db import models
from shoppay.choices import REQUEST_CHOICE, DELIVERY_STATUS_CHOICE
from shopproduct.models import Shopproduct
from shopmember.models import Shopmember

# Create your models here.
class Shoppay(models.Model):
    paynum = models.AutoField(verbose_name="주문번호", primary_key=True)
    prodnum = models.ForeignKey(Shopproduct,verbose_name="상품정보", on_delete=models.CASCADE, db_column="prodnum")
    user_id = models.ForeignKey(Shopmember,verbose_name="회원정보", on_delete=models.CASCADE, db_column="user_id")
    prodcount = models.IntegerField(verbose_name="주문개수", null=False)
    prodsize = models.CharField(verbose_name="상품사이즈",max_length=100, null=False)
    prodcolor = models.CharField(verbose_name="상품색깔",max_length=100, null=False)


class Shoppaydetail(models.Model):
    paydetailnum = models.AutoField(verbose_name="결제번호", primary_key=True)
    prodnum = models.IntegerField(verbose_name="상품번호", null=False)
    user_id = models.CharField(max_length=100, verbose_name="주문자 아이디", null=False)
    user_name = models.CharField(max_length=100, verbose_name="주문자",null=False)
    user_tel = models.CharField(max_length=100, verbose_name="주문자 전화번호",null=False)
    addressee = models.CharField(max_length=100, verbose_name="수취인",null=False)# 수취인(택배받는 사람)
    addressee_tel = models.CharField(max_length=100, verbose_name="수취인 전화번호",null=False)# 수취인(택배받는 사람)
    user_addr = models.CharField(max_length=1000, verbose_name="주소", null=False) #주소
    user_addrt = models.CharField(max_length=1000, verbose_name="상세 주소", null=False) #상세주소
    prodmainimg = models.CharField(max_length=100, verbose_name="상품 이미지")
    prodname = models.CharField(max_length=100, verbose_name="상품이름",null=False)
    prodoption = models.CharField(max_length=100, verbose_name="상품옵션", null=False)
    prodprice = models.IntegerField(verbose_name="상품가격",null=False)
    prodcount = models.IntegerField(verbose_name="구매개수",null=False)
    paytype = models.CharField(max_length=1000, verbose_name="결제수단", null=False) #결제수단
    paycommant = models.CharField(choices= REQUEST_CHOICE, max_length=1000, verbose_name="배송요청사항") #구매시 요청사항
    common_door= models.CharField(max_length=1000, verbose_name="공동현관비밀번호", default="0")
    total_pay = models.IntegerField(verbose_name = "총 결제금액", null=False) #총 결제금액
    payreg_date = models.DateTimeField(auto_now_add=True, verbose_name="결제일", blank=True) #결제일
    delively_status = models.CharField(choices=DELIVERY_STATUS_CHOICE, max_length=1000, verbose_name="배송상태", default="결제완료")#배송상태
    
class Paydata(models.Model):
    paynum = models.AutoField(verbose_name="주문번호", primary_key=True)
    prodnum = models.ForeignKey(Shopproduct,verbose_name="상품정보", on_delete=models.CASCADE, db_column="prodnum")
    user_id = models.ForeignKey(Shopmember,verbose_name="회원정보", on_delete=models.CASCADE, db_column="user_id")
    prodcount = models.IntegerField(verbose_name="주문개수", null=False)
    prodsize = models.CharField(verbose_name="상품사이즈",max_length=100, null=False)
    prodcolor = models.CharField(verbose_name="상품색깔",max_length=100, null=False)