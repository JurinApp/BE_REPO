from django.contrib import admin

from jurin.users.models import VerificationCode

# @TODO: 어드민 페이지 구축 전 인증코드 생성을 위한 임시 어드민 페이지
admin.site.register(VerificationCode)
