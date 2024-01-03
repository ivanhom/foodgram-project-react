from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import MyUser, Subscription


class MyUserAdmin(UserAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name',
        'last_name', 'is_staff', 'is_active'
    )
    search_fields = ('username', 'email')
    list_editable = ('is_staff',)
    list_filter = ('is_staff', 'is_active')
    list_display_links = ('username',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'user_email', 'subscribed', 'subscribed_email'
    )
    search_fields = (
        'user__username', 'user__email',
        'subscribed__username', 'subscribed__email'
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'

    def subscribed_email(self, obj):
        return obj.subscribed.email
    subscribed_email.short_description = 'Subscribed Email'


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
