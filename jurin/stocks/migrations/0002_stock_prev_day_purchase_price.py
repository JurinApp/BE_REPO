# Generated by Django 4.2.9 on 2024-02-07 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='prev_day_purchase_price',
            field=models.PositiveIntegerField(default=0, verbose_name='전날 매수가'),
            preserve_default=False,
        ),
    ]