import io
import os
import sys

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import serializers

from Dating import settings
from user.models import User
from user.serializers import UserSerializer


class RegisterSerializer(UserSerializer):
    password = serializers.CharField(min_length=8, max_length=128, write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'gender', 'avatar', ]

    def create(self, validated_data):
        try:
            base_avatar = Image.open(validated_data["avatar"])
            watermark = Image.open(os.path.join(os.path.dirname(settings.MEDIA_ROOT), 'media', 'water_mark.png'))
            base_avatar.paste(watermark, (0, 0), mask=watermark)
            output = io.BytesIO()
            base_avatar.save(output, format='JPEG')
            output.seek(0)
            validated_data["avatar"] = InMemoryUploadedFile(output, 'ImageField', 'avatar.jpg', 'image/jpeg',
                                                            sys.getsizeof(output), None)
        except KeyError:
            pass
        return User.objects.create_user(**validated_data)
