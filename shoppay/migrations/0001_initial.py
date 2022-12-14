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
            name='Shoppaydetail',
            fields=[
                ('paydetailnum', models.AutoField(primary_key=True, serialize=False, verbose_name='결제번호')),
                ('prodnum', models.IntegerField(verbose_name='상품번호')),
                ('user_id', models.CharField(max_length=100, verbose_name='주문자 아이디')),
                ('user_name', models.CharField(max_length=100, verbose_name='주문자')),
                ('user_tel', models.CharField(max_length=100, verbose_name='주문자 전화번호')),
                ('addressee', models.CharField(max_length=100, verbose_name='수취인')),
                ('addressee_tel', models.CharField(max_length=100, verbose_name='수취인 전화번호')),
                ('user_addr', models.CharField(max_length=1000, verbose_name='주소')),
                ('user_addrt', models.CharField(max_length=1000, verbose_name='상세 주소')),
                ('prodmainimg', models.CharField(max_length=100, verbose_name='상품 이미지')),
                ('prodname', models.CharField(max_length=100, verbose_name='상품이름')),
                ('prodoption', models.CharField(max_length=100, verbose_name='상품옵션')),
                ('prodprice', models.IntegerField(verbose_name='상품가격')),
                ('prodcount', models.IntegerField(verbose_name='구매개수')),
                ('paytype', models.CharField(max_length=1000, verbose_name='결제수단')),
                ('paycommant', models.CharField(choices=[('요청사항 없음', '요청사항 없음'), ('초인종 누르지 말아주세요', '초인종 누르지 말아주세요'), ('문 앞에 보관해주세요.', '문 앞에 보관해주세요.'), ('경비실에 맡겨주세요.', '경비실에 맡겨주세요.'), ('던지지 말아주세요!', '던지지 말아주세요!'), ('당사자 대면 전달 부탁드립니다', '당사자 대면 전달 부탁드립니다')], max_length=1000, verbose_name='배송요청사항')),
                ('common_door', models.CharField(max_length=1000, verbose_name='공동현관비밀번호')),
                ('total_pay', models.IntegerField(verbose_name='총 결제금액')),
                ('payreg_date', models.DateTimeField(auto_now_add=True, verbose_name='결제일')),
                ('delively_status', models.CharField(choices=[('결제완료', '결제완료'), ('배송준비', '배송준비'), ('배송중', '배송중'), ('배송완료', '배송완료'), ('반품진행중', '반품진행중'), ('반품완료', '반품완료')], default='결제완료', max_length=1000, verbose_name='배송상태')),
            ],
        ),
        migrations.CreateModel(
            name='Shoppay',
            fields=[
                ('paynum', models.AutoField(primary_key=True, serialize=False, verbose_name='주문번호')),
                ('prodcount', models.IntegerField(verbose_name='주문개수')),
                ('prodsize', models.CharField(max_length=100, verbose_name='상품사이즈')),
                ('prodcolor', models.CharField(max_length=100, verbose_name='상품색깔')),
                ('prodnum', models.ForeignKey(db_column='prodnum', on_delete=django.db.models.deletion.CASCADE, to='shopproduct.shopproduct', verbose_name='상품정보')),
                ('user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='shopmember.shopmember', verbose_name='회원정보')),
            ],
        ),
        migrations.CreateModel(
            name='Paydata',
            fields=[
                ('paynum', models.AutoField(primary_key=True, serialize=False, verbose_name='주문번호')),
                ('prodcount', models.IntegerField(verbose_name='주문개수')),
                ('prodsize', models.CharField(max_length=100, verbose_name='상품사이즈')),
                ('prodcolor', models.CharField(max_length=100, verbose_name='상품색깔')),
                ('prodnum', models.ForeignKey(db_column='prodnum', on_delete=django.db.models.deletion.CASCADE, to='shopproduct.shopproduct', verbose_name='상품정보')),
                ('user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='shopmember.shopmember', verbose_name='회원정보')),
            ],
        ),
    ]
