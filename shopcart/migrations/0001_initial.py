# Generated by Django 4.1 on 2022-10-05 05:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shopproduct', '0001_initial'),
        ('shopmember', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shopcartpay',
            fields=[
                ('cartpaynum', models.AutoField(primary_key=True, serialize=False, verbose_name='주문번호')),
                ('prodcount', models.IntegerField(verbose_name='주문개수')),
                ('prodsize', models.CharField(max_length=100, verbose_name='상품사이즈')),
                ('prodcolor', models.CharField(max_length=100, verbose_name='상품색깔')),
                ('prodnum', models.ForeignKey(db_column='prodnum', on_delete=django.db.models.deletion.CASCADE, to='shopproduct.shopproduct', verbose_name='상품번호')),
                ('user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='shopmember.shopmember', verbose_name='회원정보')),
            ],
        ),
        migrations.CreateModel(
            name='Shopcart',
            fields=[
                ('cartnum', models.AutoField(primary_key=True, serialize=False, verbose_name='카트번호')),
                ('prodcount', models.IntegerField(default=0, verbose_name='개수')),
                ('prodcolor', models.CharField(max_length=100, verbose_name='상품색상')),
                ('prodsize', models.CharField(max_length=100, verbose_name='상품사이즈')),
                ('prodnum', models.ForeignKey(db_column='prodnum', on_delete=django.db.models.deletion.CASCADE, to='shopproduct.shopproduct')),
                ('user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='shopmember.shopmember')),
            ],
        ),
    ]
