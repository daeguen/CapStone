from django.db import models
from shopmember.choices import GENDER_CHOICE
from shopproduct.models import Shopproduct

# Create your models here.
class Shopmember(models.Model):
    user_id = models.CharField(max_length=100, verbose_name="아이디", primary_key=True)
    user_passwd = models.CharField(max_length=100, verbose_name="비밀번호", null=False)
    user_name = models.CharField(max_length=100, verbose_name="이름", null=False)
    user_tel = models.CharField(max_length=30, verbose_name="전화번호", null=False)
    user_email = models.CharField(max_length=100, verbose_name="이메일", null=False, default='')
    user_addr = models.CharField(max_length=1000, verbose_name="주소", null=False)
    user_addrt = models.CharField(max_length=1000, verbose_name="상세 주소", null=False)
    user_gender = models.CharField(choices=GENDER_CHOICE, max_length=100, verbose_name="성별", null=False)
    user_brand = models.CharField(max_length=100, verbose_name="선호 브렌드", null=True)
    
class Shopmemberdelete(models.Model):
    user_id = models.CharField(max_length=100, verbose_name="아이디")
    user_passwd = models.CharField(max_length=100, verbose_name="비밀번호", null=False)
    user_name = models.CharField(max_length=100, verbose_name="이름", null=False)
    user_tel = models.CharField(max_length=30, verbose_name="전화번호", null=False)
    user_email = models.CharField(max_length=100, verbose_name="이메일", null=False, default='')
    user_addr = models.CharField(max_length=1000, verbose_name="주소", null=False)
    user_addrt = models.CharField(max_length=1000, verbose_name="상세 주소", null=False)
    user_gender = models.CharField(choices=GENDER_CHOICE, max_length=100, verbose_name="성별", null=False)
    user_brand = models.CharField(max_length=100, verbose_name="선호 브렌드", null=True)
    
class Shoprecome(models.Model):
    prodnum = models.ForeignKey(Shopproduct, verbose_name = "상품번호", on_delete=models.CASCADE, db_column="prodnum")