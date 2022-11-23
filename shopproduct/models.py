from django.db import models
from shopproduct.choices import BRAND_CHOICE, STATUS_CHOICE, iten_CHOICE

# Create your models here.

class Shopproduct(models.Model):
    prodnum = models.AutoField(verbose_name="상품번호", primary_key=True)
    prodname = models.CharField(max_length=100, verbose_name="상품이름", null=True)
    prodprice = models.IntegerField(verbose_name="상품가격")
    prodquantity = models.IntegerField(verbose_name="상품재고")
    prodbrand = models.CharField(verbose_name="상품 브랜드", choices=BRAND_CHOICE, max_length=100, null=False)
    proditems = models.CharField(verbose_name="상품종류", choices=iten_CHOICE, max_length=100, null=False)
    prodmainimg = models.ImageField(verbose_name="상품 메인이미지", upload_to="brandimgs")
    prodsubimg1 = models.ImageField(verbose_name="상품 서브이미지1", upload_to="brandimgs")
    prodsubimg2 = models.ImageField(verbose_name="상품 서브이미지2", upload_to="brandimgs", null=True)
    prodcontentimg = models.ImageField(verbose_name="상품 설명이미지", upload_to="brandimgs")
    prodreadcount = models.IntegerField(verbose_name="상품 조회수", default=0)
    prodstatus = models.CharField(verbose_name="상품상태", choices=STATUS_CHOICE, max_length=100)