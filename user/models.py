import io
import os
import sys

from PIL import Image
from django.contrib.auth import password_validation
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from Dating import settings


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
    liked = models.ManyToManyField("self", related_name='likes', symmetrical=False, blank=True)

    longitude = models.SmallIntegerField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    latitude = models.SmallIntegerField(validators=[MinValueValidator(-90), MaxValueValidator(90)])

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def save(self, *args, **kwargs):
        base_avatar = Image.open(self.avatar)
        watermark = Image.open(os.path.join(os.path.dirname(settings.MEDIA_ROOT), 'media', 'water_mark.png'))
        base_avatar.paste(watermark, (0, 0), mask=watermark)
        output = io.BytesIO()
        base_avatar.save(output, format='JPEG')
        output.seek(0)
        self.avatar = InMemoryUploadedFile(output, 'ImageField', f'avatar_{self.last_name}.jpg', 'image/jpeg',
                                           sys.getsizeof(output), None)
        super().save(*args, **kwargs)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None

    def __str__(self):
        return f"{self.email}"

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def like_user(self, user):
        return self.liked.add(user)

    def remove_like_user(self, user):
        return self.liked.remove(user)

    def has_liked_user(self, user):
        return self.liked.filter(pk=user.pk).exists()
