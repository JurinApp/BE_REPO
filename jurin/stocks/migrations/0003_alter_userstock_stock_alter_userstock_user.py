# Generated by Django 4.2.11 on 2024-03-27 19:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stocks', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstock',
            name='stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_stocks_info_pivot', to='stocks.stock', verbose_name='주식 고유 아이디'),
        ),
        migrations.AlterField(
            model_name='userstock',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_stocks_info_pivot', to=settings.AUTH_USER_MODEL, verbose_name='유저 고유 아이디'),
        ),
    ]
