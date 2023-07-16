import datetime

from django.core.mail import EmailMultiAlternatives
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response

from Dating.settings import EMAIL_HOST_USER
from user.models import User
from user.permissions import MyUserPermission
from user.serializers import UserSerializer


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


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ('patch', 'get', 'delete', 'put', 'post')
    permission_classes = (MyUserPermission,)
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.exclude(is_superuser=True)

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
