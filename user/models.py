from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "user_{0}/{1}".format(instance.email, filename)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if email is None:
            raise TypeError('Users must have an email.')
        if password is None:
            raise TypeError('User must have an password.')

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        if password is None:
            raise TypeError('Superusers must have a password.')
        if email is None:
            raise TypeError('Superusers must have an email.')
        user = self.create_user(email, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    MALE = 'm'
    FEMALE = 'f'
    GENDERS_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=GENDERS_CHOICES)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to=user_directory_path, default='default.jpg')

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    # EMAIL_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return f"{self.email}"

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
