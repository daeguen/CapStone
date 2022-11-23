# Generated by Django 4.1 on 2022-10-05 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Shopproduct',
            fields=[
                ('prodnum', models.AutoField(primary_key=True, serialize=False, verbose_name='상품번호')),
                ('prodname', models.CharField(max_length=100, null=True, verbose_name='상품이름')),
                ('prodprice', models.IntegerField(verbose_name='상품가격')),
                ('prodquantity', models.IntegerField(verbose_name='상품재고')),
                ('prodbrand', models.CharField(choices=[('아디다스', '아디다스'), ('뉴발란스', '뉴발란스'), ('나이키', '나이키'), ('노스페이스', '노스페이스'), ('스파오', '스파오'), ('HnM', 'HnM'), ('캉골', '캉골'), ('무지', '무지')], max_length=100, verbose_name='상품 브랜드')),
                ('proditems', models.CharField(choices=[('반팔티', '반팔티'), ('긴팔티', '긴팔티'), ('아우터', '아우터'), ('반바지', '반바지'), ('긴바지', '긴바지'), ('치마', '치마'), ('신발', '신발'), ('한벌옷', '한벌옷')], max_length=100, verbose_name='상품종류')),
                ('prodmainimg', models.ImageField(upload_to='brandimgs', verbose_name='상품 메인이미지')),
                ('prodsubimg1', models.ImageField(upload_to='brandimgs', verbose_name='상품 서브이미지1')),
                ('prodsubimg2', models.ImageField(null=True, upload_to='brandimgs', verbose_name='상품 서브이미지2')),
                ('prodcontentimg', models.ImageField(upload_to='brandimgs', verbose_name='상품 설명이미지')),
                ('prodreadcount', models.IntegerField(default=0, verbose_name='상품 조회수')),
                ('prodstatus', models.CharField(choices=[('재고있음', '재고있음'), ('품절', '품절')], max_length=100, verbose_name='상품상태')),
            ],
        ),
    ]
