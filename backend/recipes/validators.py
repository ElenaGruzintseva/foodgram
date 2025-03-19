from django.conf import settings
from django.core.exceptions import ValidationError


def validate_username(username):
    if username == settings.USER_PROFILE_URL:
        raise ValidationError(
            (f'Использовать имя {settings.USER_PROFILE_URL} '
             'в качестве username запрещено!')
        )
