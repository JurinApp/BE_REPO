from django.urls import path

from jurin.authentication.apis import JWTRefreshAPI, SignInAPI, SignUpAPI, ValidateAPI

urlpatterns = [
    path("/signup", SignUpAPI.as_view(), name="auth_signup"),
    path("/signin", SignInAPI.as_view(), name="auth_signin"),
    path("/jwt/refresh", JWTRefreshAPI.as_view(), name="auth_jwt_refresh"),
    path("/validate", ValidateAPI.as_view(), name="auth_validate"),
]
