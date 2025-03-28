from django.db.models import Count, F, Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.urls import reverse
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeGETSerializer,
    ShoppingListSerializer,
    SubscriptionSerializer,
    SubscribeCreateSerializer,
    TagSerializer,
)
from .data_handlers import (
    add_favorite_or_shopping_list,
    generate_shopping_list_pdf,
    remove_favorite_or_shopping_list,
)
from .pagination import CustomPagination
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag,
)
from users.models import Subscribe, User


class UserViewSet(DjoserUserViewSet):
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=('put',),
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        serializer = AvatarSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        request.user.avatar.delete()
        request.user.avatar = None
        request.user.save()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=[IsAuthenticated],
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscriptions_from__user=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=('post',),
        url_path='subscribe',
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        serializer = SubscribeCreateSerializer(
            data={'user': request.user.pk, 'author': author.pk},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)

        deleted_count, _ = Subscribe.objects.filter(
            user=user, author=author
        ).delete()
        if deleted_count == 0:
            return Response(
                {'ошибка': 'Вы не подписаны на этого автора.'},
                status=HTTP_400_BAD_REQUEST,
            )

        return Response(status=HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):

    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = Recipe.objects.select_related(
            'author'
        ).prefetch_related('tags', 'ingredients')

        if user_id is not None:
            queryset = queryset.favorited(user_id).in_shopping_cart(user_id)

        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'get-link'):
            return RecipeGETSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        permission_classes=(AllowAny,),
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        return Response({'short-link': request.build_absolute_uri(reverse(
            'recipes:shortlink', args=[recipe.pk]))}, status=HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return add_favorite_or_shopping_list(
                request, FavoriteSerializer, pk
            )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return remove_favorite_or_shopping_list(
            request, FavoriteRecipe, pk
        )

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return add_favorite_or_shopping_list(
                request, ShoppingListSerializer, pk
            )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return remove_favorite_or_shopping_list(
            request, ShoppingList, pk
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = request.user

        recipes_in_shopping_list = (
            RecipeIngredient.objects.filter(
                recipe__shopping_lists__user=user
            ).values(
                ingredient_name=F('ingredient__name'),
                measurement_unit=F('ingredient__measurement_unit'),
            )
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient_name')
        )

        pdf_buffer = generate_shopping_list_pdf(recipes_in_shopping_list)

        response = FileResponse(pdf_buffer, content_type='application/pdf')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.pdf"'
        return response
