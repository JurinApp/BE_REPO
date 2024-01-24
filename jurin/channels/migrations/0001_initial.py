# Generated by Django 4.2.9 on 2024-02-03 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='채널 고유 아이디')),
                ('name', models.CharField(max_length=16, verbose_name='채널 이름')),
                ('entry_code', models.CharField(max_length=8, unique=True, verbose_name='참여 코드')),
                ('is_pending_deleted', models.BooleanField(default=False, verbose_name='삭제 대기 여부')),
                ('pending_deleted_at', models.DateTimeField(null=True, verbose_name='삭제 대기 일시')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='삭제 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성 일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정 일시')),
            ],
            options={
                'verbose_name': 'channel',
                'verbose_name_plural': 'channels',
                'db_table': 'channel',
            },
        ),
        migrations.CreateModel(
            name='UserChannel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='유저 채널 고유 아이디')),
                ('point', models.PositiveIntegerField(default=0, verbose_name='포인트')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='삭제 여부')),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_channel_pivot', to='channels.channel', verbose_name='채널 고유 아이디')),
            ],
            options={
                'verbose_name': 'user channel',
                'verbose_name_plural': 'user channels',
                'db_table': 'user_channel',
            },
        ),
    ]
