# Generated by Django 4.2.9 on 2024-03-07 00:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('channels', '0002_initial'),
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertradeinfo',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_trade_info_pivot', to=settings.AUTH_USER_MODEL, verbose_name='유저 고유 아이디'),
        ),
        migrations.AddField(
            model_name='userstock',
            name='stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_stocks', to='stocks.stock', verbose_name='주식 고유 아이디'),
        ),
        migrations.AddField(
            model_name='userstock',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_stocks', to=settings.AUTH_USER_MODEL, verbose_name='유저 고유 아이디'),
        ),
        migrations.AddField(
            model_name='stock',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stocks', to='channels.channel', verbose_name='채널 고유 아이디'),
        ),
        migrations.AddField(
            model_name='stock',
            name='user_trade_info',
            field=models.ManyToManyField(related_name='stock', through='stocks.UserTradeInfo', to=settings.AUTH_USER_MODEL, verbose_name='유저 주식 정보'),
        ),
        migrations.AddField(
            model_name='dailyprice',
            name='stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_prices', to='stocks.stock', verbose_name='주식 고유 아이디'),
        ),
        migrations.AlterUniqueTogether(
            name='userstock',
            unique_together={('stock', 'user')},
        ),
        migrations.AddIndex(
            model_name='dailyprice',
            index=models.Index(fields=['trade_date'], name='daily_price_trade_d_1daca7_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='dailyprice',
            unique_together={('trade_date', 'stock')},
        ),
    ]
