from django.db import models

# Create your models here.

class Shopnotice(models.Model):
    noticenum = models.AutoField(verbose_name="공지번호", primary_key=True)
    adminname = models.CharField( max_length=30, verbose_name="작성자", null=False)
    noticetitle = models.CharField( max_length=200, verbose_name="글 제목", null=False)
    noticecontent = models.TextField(verbose_name="글 내용", null=False)
    noticereadcount = models.IntegerField( verbose_name="조회수", default=0 )
    noticeregdate = models.DateTimeField( auto_now_add=True, verbose_name="작성일", blank=True )