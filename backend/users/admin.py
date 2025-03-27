from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmins

from .models import Subscribe, User

admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class UserAdmin(UserAdmins):

    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'avatar',
        'recipes_count',
        'subscriptions_count',
    )

    list_filter = ('username', 'email')
    search_fields = ('username', 'email',)

    @admin.display(description='Подписчики')
    def subscriptions_count(self, user):
        return user.subscriptions_to.count()

    @admin.display(description='Рецепты')
    def recipes_count(self, user):
        return user.recipes.count()


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):

    list_display = ('user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')
