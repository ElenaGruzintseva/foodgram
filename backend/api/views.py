from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_200_OK

from .filters import IngredientFilter, RecipeFilter
from .permissions import OwnerOnlyPermission
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeGETSerializer,
    ShoppingListSerializer,
    TagSerializer,
)
from .utils import (
    add_favorite_or_shopping_list,
    generate_shopping_list_pdf,
    remove_favorite_or_shopping_list
)
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):

    permission_classes = (OwnerOnlyPermission,)
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
            url_path="get-link"
        )
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        return Response({"short-link": request.build_absolute_uri(reverse(
            "recipes:shortlink", args=[recipe.pk]))}, status=HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        user = request.user

        if request.method == 'POST':
            return add_favorite_or_shopping_list(
                request, user, FavoriteRecipe, FavoriteSerializer, pk
            )

        elif request.method == 'DELETE':
            return remove_favorite_or_shopping_list(user, FavoriteRecipe, pk)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        user = request.user

        if request.method == 'POST':
            return add_favorite_or_shopping_list(
                request, user, ShoppingList, ShoppingListSerializer, pk
            )

        elif request.method == 'DELETE':
            return remove_favorite_or_shopping_list(user, ShoppingList, pk)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = request.user
        recipes_in_shopping_list = (
            RecipeIngredient.objects.filter(
                recipe__in_shopping_lists__user=user
            )
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )

        pdf_buffer = generate_shopping_list_pdf(recipes_in_shopping_list)

        response = HttpResponse(
            pdf_buffer.getvalue(), content_type='application/pdf'
        )
        response[
            'Content-Disposition'
        ] = "attachment; filename='shopping_list.pdf'"
        return response
