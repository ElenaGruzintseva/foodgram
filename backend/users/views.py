from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from djoser.serializers import SetPasswordSerializer
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (
    AvatarUserSerializer,
    SubscriptionCreateSerializer,
    SubscriptionSerializer,
    UserGETSerializer,
    UserCreateSerializer
)
from .models import Subscribe, User


class UserViewSet(DjoserUserViewSet):

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.request.method == 'GET':
            return UserGETSerializer
        return UserCreateSerializer

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarUserSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        request.user.avatar = None
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(authors__user=request.user)
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(
            subscriptions, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        user = request.user
        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя.')
        if request.method == 'POST':
            _, created = Subscribe.objects.get_or_create(user=user, author=author)
            if not created:
                raise ValidationError('Вы уже подписаны на этого пользователя!')
            return Response(
                SubscriptionSerializer(author, context={'request': request}).data,
                status=status.HTTP_201_CREATED,
            )
        get_object_or_404(Subscribe, user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
