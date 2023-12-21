from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models.functions import Lower

User = get_user_model()


class Tag(models.Model):
    """Модель тегов для рецептов."""
    name = models.CharField(
        verbose_name='Название тега', max_length=200, unique=True
    )
    color = models.CharField(verbose_name='Цвет', max_length=7)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        validators=(RegexValidator(
            regex=settings.TAG_SLUG_REGEX,
            message='Недопустимый символ в slug Тега'
        ),),
        help_text=(
            'Обязательное поле. Не более 200 символов. '
            'Допустимы буквы, цифры и символы: -/_.'
        )
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:20]


class Ingredient(models.Model):
    """Модель ингридиентов для рецептов."""
    name = models.CharField(
        verbose_name='Название ингредиента', max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения', max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = (Lower('name'),)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            ),
        )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Recipe(models.Model):
    """Модель рецепта."""
    tags = models.ManyToManyField(
        Tag, verbose_name='Теги', related_name='recipes'
    )
    author = models.ForeignKey(
        User, verbose_name='Автор',
        related_name='recipes', on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиенты',
        related_name='recipe', through='RecipeIngredient'
    )
    name = models.CharField(
        verbose_name='Название рецепта', max_length=200
    )
    image = models.ImageField(
        verbose_name='Картинка рецепта',
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(MinValueValidator(
            limit_value=1,
            message='Время приготовления не может быть менее 1 минуты.'),
        )
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации рецепта', auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:20]


class RecipeIngredient(models.Model):
    """Вспомогательная модель для хранения
    количества ингредиента для рецепта.
    """
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='res'
    )

    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(MinValueValidator(
            limit_value=0.5,
            message='Количество должно быть больше нуля'),
        )
    )

    class Meta:
        verbose_name = 'Количество ингредиента для рецепта'
        verbose_name_plural = 'Количество ингредиентов для рецепта'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        return (
            f'Для {self.recipe} требуется {self.ingredient.name}: '
            f'{self.amount} {self.ingredient.measurement_unit}'
        )


class FavoriteRecipe(models.Model):
    """Модель для хранения избранных рецептов."""
    user = models.ForeignKey(
        User, verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_favorite'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    """Модель для хранения избранных рецептов."""
    user = models.ForeignKey(
        User, verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_shopping_cart'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe}'
