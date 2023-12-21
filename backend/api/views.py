from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import RecipeFilter
from api.messages import INVALID_TOKEN_ERR
from api.serializers import IngredientSerializer, FavoriteRecipeSerializer, ShoppingCartSerializer, FollowUserSerializer, ReadRecipeSerializer, WriteRecipeSerializer, ReadRecipeIngredientSerializer, WriteRecipeIngredientSerializer, TagSerializer, UsersSerializer
from api.permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrJustReadingRecipe, IsSuperUserOrAdmin, IsUserOrAdminOrJustReadingUserdata
from recipes.models import Ingredient, Recipe, FavoriteRecipe, RecipeIngredient, Tag, User, ShoppingCart
from users.models import Subscription


class UsersViewSet(UserViewSet):
    """ViewSet для модели User. Присутствуют эндпоинты для просмотра подписок
    пользователя и возможности подписки на любого пользователя.
    """
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (AllowAny,)

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            self.permission_classes = (IsUserOrAdminOrJustReadingUserdata,)
        return super().get_permissions()

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(subscribed__user=user)
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = FollowUserSerializer(
                page, many=True,
                context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = FollowUserSerializer(
            subscriptions, many=True,
            context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = request.user
        subscribed = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=user, subscribed=subscribed)

        if request.method == 'POST':
            if subscription.exists():
                return Response({'Вы уже подписаны на данного пользователя!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user == subscribed:
                return Response({'Нельзя подписаться на самого себя!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowUserSerializer(
                subscribed, context={'request': request}
            )
            Subscription.objects.create(user=user, subscribed=subscribed)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response({'Вы отписались от данного пользователя!'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'Вы не были подписаны на этого пользователя!'}, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Tag. Выводит список тегов при GET-запросе."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Ingredient. Выводит список ингредиентов при
    GET-запросе. Поддерживается фильтр по названию ингредиента.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)



class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Recipe."""
    queryset = Recipe.objects.all()
    serializer_class = WriteRecipeSerializer
    permission_classes = (IsAuthorOrAdminOrJustReadingRecipe,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def create(self, request, *args, **kwargs):
        ingredients = self.request.data.get('ingredients')
        tags = self.request.data.get('tags')
        tag_list = []
        if not ingredients:
            return Response({'В рецепте должен быть минимум 1 ингредиент!'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not tags:
            return Response({'В рецепта должен быть минимум 1 тег!'},
                            status=status.HTTP_400_BAD_REQUEST)
        for tag in tags:
            if tag in tag_list:
                return Response({'Теги в списке не должны повторяться!'},
                                status=status.HTTP_400_BAD_REQUEST)
            tag_list.append(tag)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        ingredients = self.request.data.get('ingredients')
        tags = self.request.data.get('tags')
        tag_list = []
        if not ingredients:
            return Response({'В рецепте должен быть минимум 1 ингредиент!'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not tags:
            return Response({'В рецепта должен быть минимум 1 тег!'},
                            status=status.HTTP_400_BAD_REQUEST)
        for tag in tags:
            if tag in tag_list:
                return Response({'Теги в списке не должны повторяться!'},
                                status=status.HTTP_400_BAD_REQUEST)
            tag_list.append(tag)
        return super().update(request, *args, **kwargs)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        user = request.user
        try:
            recipe = Recipe.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({'Такого рецепта не существует'},
                            status=status.HTTP_400_BAD_REQUEST)
        favorite_recipe = FavoriteRecipe.objects.filter(
            user=user, recipe=recipe)

        if request.method == 'POST':
            if favorite_recipe.exists():
                return Response({'Вы уже добавили в избранное данный рецепт!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteRecipeSerializer(
                recipe, context={'request': request}
            )
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if favorite_recipe.exists():
                favorite_recipe.delete()
                return Response({'Вы удалили рецепт из избранного!'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'Вы не добавляли данный рецепт в избранное!'}, status=status.HTTP_400_BAD_REQUEST)
      
    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        user = request.user
        try:
            recipe = Recipe.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({'Такого рецепта не существует'},
                            status=status.HTTP_400_BAD_REQUEST)
        shopped_recipe = ShoppingCart.objects.filter(user=user, recipe=recipe)

        if request.method == 'POST':
            if shopped_recipe.exists():
                return Response({'Вы уже добавили в корзину данный рецепт!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(
                recipe, context={'request': request}
            )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if shopped_recipe.exists():
                shopped_recipe.delete()
                return Response({'Вы удалили рецепт из корзины!'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'Вы не добавляли данный рецепт в корзину!'}, status=status.HTTP_400_BAD_REQUEST)
        


