from rest_framework import serializers

from user.models import User
from user.serializers import UserSerializer


class RegisterSerializer(UserSerializer):
    password = serializers.CharField(min_length=8, max_length=128, write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'gender', 'avatar', ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
