from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Subscribe, User

admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class MyUserAdmin(UserAdmin):

    list_display = ('username', 'first_name', 'last_name', 'email', 'avatar',)
    list_filter = ('username', 'email')
    search_fields = ('username', 'email',)


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):

    list_display = ('user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')
