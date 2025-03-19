from django.urls import path

from .views import redirect_to_recipe_detail


urlpatterns = [
    path('s/<int:pk>/', redirect_to_recipe_detail, name='shortlink'),
]
