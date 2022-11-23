from django.db import models

# Create your models here.
class Shopreview(models.Model) :
    reviewnum = models.AutoField(verbose_name="리뷰 번호", primary_key=True)
    reviewtitle = models.CharField(max_length=400, verbose_name="리뷰 제목", null=False)
    reviewcontent = models.CharField(max_length=4000, verbose_name="리뷰 내용", null=False)
    reviewimg = models.ImageField(max_length=500, verbose_name="리뷰 사진", upload_to="reviewimg", null=True)
    reviewrating = models.IntegerField(verbose_name="별점", null=False)
    reviewregdate = models.DateTimeField(auto_now_add=True, verbose_name="리뷰 작성일", blank=True)
    prodnum = models.IntegerField(verbose_name="상품번호", null=False)
    user_id = models.CharField(max_length=30, verbose_name="작성자", null=False)