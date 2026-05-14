from django.db import transaction

from apps.users.models import User
from apps.users.passwords import hash_password


@transaction.atomic
def register_user(validated_data: dict) -> User:
    password = validated_data.pop("password")
    validated_data.pop("password_repeat", None)

    user = User.objects.create(
        **validated_data,
        password_hash=hash_password(password),
    )
    return user