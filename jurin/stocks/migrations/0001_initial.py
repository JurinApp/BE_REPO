# Generated by Django 4.2.9 on 2024-03-07 00:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DailyPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='일별 시세 고유 아이디')),
                ('trade_date', models.DateField(verbose_name='거래 일자')),
                ('price', models.PositiveIntegerField(verbose_name='주가')),
                ('volume', models.PositiveIntegerField(verbose_name='거래량')),
                ('transaction_amount', models.PositiveIntegerField(verbose_name='거래 대금')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성 일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정 일시')),
            ],
            options={
                'verbose_name': 'daily price',
                'verbose_name_plural': 'daily prices',
                'db_table': 'daily_price',
            },
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='주식 고유 아이디')),
                ('name', models.CharField(max_length=32, verbose_name='종목명')),
                ('purchase_price', models.PositiveIntegerField(verbose_name='매수가')),
                ('prev_day_purchase_price', models.PositiveIntegerField(verbose_name='전날 매수가')),
                ('next_day_purchase_price', models.PositiveIntegerField(verbose_name='다음날 매수가')),
                ('tax', models.FloatField(verbose_name='세금')),
                ('standard', models.CharField(max_length=32, verbose_name='기준')),
                ('content', models.TextField(verbose_name='내용')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성 일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정 일시')),
            ],
            options={
                'verbose_name': 'stock',
                'verbose_name_plural': 'stocks',
                'db_table': 'stock',
            },
        ),
        migrations.CreateModel(
            name='UserStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='유저 주식 고유 아이디')),
                ('total_stock_amount', models.PositiveIntegerField(verbose_name='총 주식 수량')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성 일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정 일시')),
            ],
            options={
                'verbose_name': 'user stock',
                'verbose_name_plural': 'user stocks',
                'db_table': 'user_stock',
            },
        ),
        migrations.CreateModel(
            name='UserTradeInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='거래 정보 고유 아이디')),
                ('trade_date', models.DateField(verbose_name='거래 일자')),
                ('trade_type', models.IntegerField(verbose_name='거래 유형')),
                ('price', models.PositiveIntegerField(verbose_name='단가')),
                ('amount', models.PositiveIntegerField(verbose_name='수량')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_trade_info_pivot', to='stocks.stock', verbose_name='주식 고유 아이디')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성 일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정 일시')),
            ],
            options={
                'verbose_name': 'user trade info',
                'verbose_name_plural': 'user trade infos',
                'db_table': 'user_trade_info',
            },
        ),
    ]
