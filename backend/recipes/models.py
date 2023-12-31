from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

from api.messages import COOKING_TIME_ERR, INGRED_AMOUNT_ERR
from recipes.validators import MinMaxValidator

User = get_user_model()


class Tag(models.Model):
    """Модель тегов для рецептов."""
    name = models.CharField(
        verbose_name='Название тега', max_length=200, unique=True
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        validators=(RegexValidator(
            regex=settings.TAG_COLOR_REGEX,
            message='Цвет должен быть в формате Hex'
        ),),
        help_text=(
            'Обязательное поле. Например, #8000ff - это фиолетовый цвет.'
        )
    )
    slug = models.SlugField(max_length=200, unique=True)

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
        ordering = ('name'),
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='not_unique_name_measurement_unit'
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
        verbose_name='Картинка рецепта', upload_to='recipes/images/'
    )
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(MinMaxValidator(
            min_value=settings.COOKING_MIN_TIME,
            max_value=settings.COOKING_MAX_TIME,
            message=COOKING_TIME_ERR
        ),)
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
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )

    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(MinMaxValidator(
            min_value=settings.INGRED_MIN_AMOUNT,
            max_value=settings.INGRED_MAX_AMOUNT,
            message=INGRED_AMOUNT_ERR
        ),)
    )

    class Meta:
        verbose_name = 'Количество ингредиента для рецепта'
        verbose_name_plural = 'Количество ингредиентов для рецепта'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='not_unique_recipe_ingredient'
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
                name='not_unique_user_recipe_favorite'
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
                name='not_unique_user_recipe_shopping_cart'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe}'
