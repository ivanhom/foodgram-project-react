from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.forms import ValidationError


class MyUser(AbstractUser):
    """Кастомная модель пользователя."""
    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        max_length=150,
        validators=(RegexValidator(
            regex=settings.USERNAME_REGEX,
            message='Недопустимый символ в имени пользователя'
        ),),
        help_text=(
            'Обязательное поле. Не более 150 символов. '
            'Допустимы буквы, цифры и символы: @/./+/-/_.'
        )
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=254
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:20]

    @property
    def is_admin(self):
        return self.is_staff or self.is_superuser


class Subscription(models.Model):
    """Модель подписок пользователей."""
    user = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, related_name='subscriber'
    )
    subscribed = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, related_name='subscribed'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('subscribed',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'subscribed'),
                name='not_unique_user_subscribed'
            ),
        )

    def validate(self):
        if self.user == self.subscribed:
            raise ValidationError(
                'Нельзя подписаться на самого себя!'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} подписан на {self.subscribed}'
