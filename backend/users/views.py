from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet

from api.permissions import OwnerOnlyPermission
from .models import Subscribe, User
from .serializers import (
    AvatarUserSerializer,
    SubscriptionCreateSerializer,
    SubscriptionSerializer,
    UserGETSerializer
)


class MeView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserGETSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAvatar(UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = AvatarUserSerializer
    permission_classes = (OwnerOnlyPermission,)

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        instance.avatar.delete()


class SubscribeView(APIView):

    permission_classes = (IsAuthenticated,)

    def get_user_author(self, request, pk):
        user = request.user
        author = get_object_or_404(User, id=pk)
        return user, author

    def post(self, request, pk):
        user, author = self.get_user_author(request, pk)

        serializer = SubscriptionCreateSerializer(
            data={'user': user.id, 'author': author.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user, author = self.get_user_author(request, pk)

        subscribe = Subscribe.objects.filter(user=user, author=author).first()
        if subscribe:
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'ошибка': 'Вы не подписаны на этого автора.'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SubscriptionsListView(generics.ListAPIView):

    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)
