import base64

from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.messages import (INGRED_NOT_FOUND_ERR, INGRED_REPEAT_ERR,
                          TAG_NOT_FOUND_ERR, TAG_REPEAT_ERR)
from api.utils import add_ingredients_for_recipe
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag, User)


class UsersSerializer(UserSerializer):
    """Сериализатор для информации о пользователе в модели User."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.subscribed.filter(user=user).exists()


class UsersCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации нового пользователя в модели User."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}


class Base64ImageField(serializers.ImageField):
    """Сериализатор для декодирования изображения base64 для модели Recipe."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', read_only=True
    )
    name = serializers.CharField(
        source='ingredient.name', read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class WriteRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов в рецепт."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения объекта рецепта модели Recipe."""
    tags = TagSerializer(many=True)
    author = UsersSerializer(read_only=True)
    ingredients = ReadRecipeIngredientSerializer(
        many=True, source='recipe_ingredient', read_only=True
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_is_favorited(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.favorite.filter(user=user).exists()

    def get_is_in_shopping_cart(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.shopping_cart.filter(user=user).exists()


class WriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания объекта рецепта модели Recipe."""
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = WriteRecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        add_ingredients_for_recipe(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        if 'ingredients' not in validated_data:
            instance.save()
            return instance
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        add_ingredients_for_recipe(instance, ingredients)
        if 'tags' not in validated_data:
            instance.save()
            return instance
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.save()
        return instance

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if not ingredients:
            raise ValidationError(INGRED_NOT_FOUND_ERR)
        if not tags:
            raise ValidationError(TAG_NOT_FOUND_ERR)
        ingredients_list = []
        tags_list = []
        for i in ingredients:
            if i['ingredient'] in ingredients_list:
                raise ValidationError(INGRED_REPEAT_ERR)
            ingredients_list.append(i['ingredient'])
        for i in tags:
            if i in tags_list:
                raise ValidationError(TAG_REPEAT_ERR)
            tags_list.append(i)
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return ReadRecipeSerializer(instance, context=context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения краткой информации о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления или удаления избранного рецепта."""

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return ShortRecipeSerializer(instance, context=context).data


class ShoppingCartSerializer(FavoriteRecipeSerializer):
    """Сериализатор для добавления или удаления рецепта в корзине."""

    class Meta:
        model = ShoppingCart


class FollowUserSerializer(UserSerializer):
    """Сериализатор для подписки или отписки на избранного пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
            'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.subscribed.filter(user=user).exists()

    def get_recipes(self, object):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes_list = object.recipes.all()
        if recipes_limit:
            recipes_list = recipes_list[:int(recipes_limit)]
        return ShortRecipeSerializer(
            recipes_list, context={'request': request}, many=True
        ).data

    def get_recipes_count(self, object):
        return object.recipes.count()
