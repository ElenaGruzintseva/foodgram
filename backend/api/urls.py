from django.urls import include, path

from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')