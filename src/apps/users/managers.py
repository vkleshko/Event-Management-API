from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(
            self, password, phone_regex=None, email=None, phone_number=None, **extra_fields
    ):
        """
        Create and save a user with the given email and password.
        """

        if email is not None:
            email = self.normalize_email(email)
            user = self.model(email=email, **extra_fields)
        else:
            phone_regex(phone_number)
            user = self.model(phone_number=phone_number, **extra_fields)

        user.set_password(password)
        user.save()
        return user

    def create_superuser(
            self, email, password, full_name=None, phone_number=None, **extra_fields
    ):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(
            email=email, password=password, **extra_fields
        )
