import datetime
import math

from django.core.mail import EmailMultiAlternatives
from django.db.models import Count, F, Func, FloatField, Value
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response

from Dating.settings import EMAIL_HOST_USER
from user.models import User
from user.permissions import MyUserPermission
from user.serializers import UserSerializer

ARC_LENGTH = 6371


def message(sent_to_email, name_user, email_user):
    today = datetime.date.today()
    subject = f"Взаимная симпатия {today}"
    text_content = f"Взаимная симпатия"
    from_email = EMAIL_HOST_USER

    html = f'<p>Вы понравились пользователю {name_user}! Почта участника: {email_user} </p>'
    to = sent_to_email
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html, "text/html")
    msg.send()


def calculate_distance(latitude_user, longitude_user):
    latitude_user = math.radians(latitude_user)
    longitude_user = math.radians(longitude_user)
    return Value(ARC_LENGTH) * Func(
        Func(
            F("latitude") * Value(math.pi / 180),
            function="sin",
            output_field=FloatField()
        ) * Value(
            math.sin(latitude_user)
        ) + Func(
            F("latitude") * Value(math.pi / 180),
            function="cos",
            output_field=FloatField()
        ) * Value(
            math.cos(latitude_user)
        ) * Func(
            Value(longitude_user) - F("longitude") * Value(math.pi / 180),
            function="cos",
            output_field=FloatField()
        ),
        function="acos"
    )


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ('patch', 'get', 'delete', 'put', 'post')
    permission_classes = (MyUserPermission,)
    serializer_class = UserSerializer
    filterset_fields = ('gender', 'first_name', 'last_name')

    def get_queryset(self):
        likes_count = self.request.query_params.get('likes_count')
        distance = self.request.query_params.get('distance')
        queryset = User.objects.all().annotate(likes_count=Count("liked"))
        if not self.request.user.is_anonymous:
            queryset = queryset.annotate(
                distance=calculate_distance(self.request.user.latitude, self.request.user.longitude))
        if not self.request.user.is_superuser:
            queryset = queryset.exclude(is_superuser=True)
        if likes_count is not None:
            queryset = queryset.filter(likes_count=likes_count)
        if distance is not None and not self.request.user.is_anonymous:
            queryset = queryset.filter(distance__lte=distance)
        return queryset

    @action(methods=['post'], detail=True)
    def like(self, request, *args, **kwargs):
        user = self.get_object()
        user_likes = self.request.user
        user_likes.like_user(user)
        serializer = self.serializer_class(user, context={'request': request})
        if user.has_liked_user(user_likes):
            message(user_likes.email, user.name, user.email)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def remove_like(self, request, *args, **kwargs):
        user = self.get_object()
        user_likes = self.request.user
        user_likes.remove_like_user(user)
        serializer = self.serializer_class(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
