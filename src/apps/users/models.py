from django.db import models
from .managers import CustomUserManager
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=500, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
