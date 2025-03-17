from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)
from users.views import (
    MeView,
    SubscriptionsListView,
    SubscribeView,
    UserAvatar,
    UserViewSet
)

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')


user_urls = [
    path('me/', MeView.as_view(), name='user-me'),
    path(
        'subscriptions/',
        SubscriptionsListView.as_view(),
        name='subscriptions-list',
    ),
    path('<int:pk>/subscribe/', SubscribeView.as_view(), name='subscribe'),
    path(
        'me/avatar/',
        UserAvatar.as_view({'put': 'update', 'delete': 'destroy'}),
        name='user-avatar'),
]

urlpatterns = [
    path('users/', include(user_urls)),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
