# Generated by Django 4.2.9 on 2024-02-03 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='아이템 고유 아이디')),
                ('title', models.CharField(max_length=32, verbose_name='제목')),
                ('content', models.TextField(verbose_name='내용')),
                ('image_url', models.URLField(max_length=512, verbose_name='이미지 URL')),
                ('amount', models.PositiveIntegerField(verbose_name='수량')),
                ('price', models.PositiveIntegerField(verbose_name='가격')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='삭제 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성 일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정 일시')),
            ],
            options={
                'verbose_name': 'item',
                'verbose_name_plural': 'items',
                'db_table': 'item',
            },
        ),
        migrations.CreateModel(
            name='UserItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='유저 아이템 고유 아이디')),
                ('is_used', models.BooleanField(default=False, verbose_name='사용 여부')),
                ('used_at', models.DateTimeField(null=True, verbose_name='사용 일시')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_item_pivot', to='items.item', verbose_name='아이템 고유 아이디')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성 일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정 일시')),
            ],
            options={
                'verbose_name': 'user item',
                'verbose_name_plural': 'user items',
                'db_table': 'user_item',
            },
        ),
    ]
