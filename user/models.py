from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):

    def create_user(self, username="", email=None, password=None, **extra_fields):
        username = "default"
        super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username="", email=None, password=None, **extra_fields):
        username = "default"
        super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):

    username = models.CharField(_('username'), max_length=150, unique=False, blank=True)
    first_name = models.CharField(_('first name'), max_length=150)
    middle_name = models.CharField(_('middle name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(_('phone number'), max_length=11, unique=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []