from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)
from users.views import (UserViewSet)

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
