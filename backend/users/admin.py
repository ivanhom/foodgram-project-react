from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import MyUser, Subscription  # isort:skip


class MyUserAdmin(UserAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name',
        'last_name', 'is_staff', 'is_active'
    )
    search_fields = ('username', 'email')
    list_editable = ('is_staff',)
    list_filter = ('is_staff', 'is_active', 'email', 'username')
    list_display_links = ('username',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subscribed')
    search_fields = ('user', 'subscribed')
    list_filter = ('user',)


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
