from django.db import models

# Create your models here.
class Shopqna(models.Model):
    qnanum = models.AutoField(verbose_name="qna번호", primary_key=True)
    user_id = models.CharField(max_length=30, verbose_name="작성자", null=False)
    qnatitle = models.CharField(max_length=200, verbose_name="글 제목", null=False)
    qnacontent = models.TextField(verbose_name="글 내용", null=False)
    qnareadcount = models.IntegerField(verbose_name="조회수", default=0)
    qnaregdate = models.DateTimeField(auto_now_add=True, verbose_name="작성일", blank=True)
    repleadmin = models.CharField(max_length=50, verbose_name="답변작성자", null=True)
    replecontent = models.TextField(verbose_name="답변글 내용", null=True)
    repleregdate = models.DateTimeField(auto_now_add=True, verbose_name="답변 작성일", blank=True)