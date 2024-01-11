# Generated by Django 4.2.9 on 2024-02-03 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerificationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='인증 코드 고유 아이디')),
                ('code', models.CharField(max_length=8, unique=True, verbose_name='인증 코드')),
                ('is_verified', models.BooleanField(default=False, verbose_name='인증 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성 일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정 일시')),
            ],
            options={
                'verbose_name': 'verification code',
                'verbose_name_plural': 'verification codes',
                'db_table': 'verification_code',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='유저 고유 아이디')),
                ('username', models.CharField(max_length=32, unique=True, verbose_name='유저 아이디')),
                ('nickname', models.CharField(max_length=8, verbose_name='닉네임')),
                ('school_name', models.CharField(max_length=16, null=True, verbose_name='학교 이름')),
                ('password', models.CharField(max_length=128, verbose_name='비밀번호')),
                ('is_active', models.BooleanField(default=True, verbose_name='활성화 여부')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='탈퇴 여부')),
                ('is_admin', models.BooleanField(default=False, verbose_name='관리자 여부')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='탈퇴 일시')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성 일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정 일시')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'db_table': 'user',
            },
        ),
    ]
