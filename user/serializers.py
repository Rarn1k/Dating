from rest_framework import serializers
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    liked = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    distance = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    def get_liked(self, instance):
        request = self.context.get('request', None)
        if request is None or request.user.is_anonymous:
            return False
        return request.user.has_liked_user(instance)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'gender', 'email', 'avatar', 'liked', 'likes_count', 'distance']
