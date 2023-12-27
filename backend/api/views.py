from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.messages import (RECIPE_ALR_ADDED_ERR, RECIPE_NOT_ADDED_ERR,
                          RECIPE_NOT_FOUND_ERR, SUBSCR_ALR_ERR,
                          SUBSCR_NOT_FOUND_ERR, SUBSCR_NOT_YOURSELF_ERR)
from api.paginators import LimitPagination
from api.permissions import (IsAuthorOrAdminOrJustReadingRecipe,
                             IsUserOrAdminOrJustReadingUserdata)
from api.serializers import (FavoriteRecipeSerializer, FollowUserSerializer,
                             IngredientSerializer, ShoppingCartSerializer,
                             TagSerializer, UsersSerializer,
                             WriteRecipeSerializer)
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag, User)
from users.models import Subscription


class UsersViewSet(UserViewSet):
    """ViewSet для модели User. Присутствуют эндпоинты для просмотра подписок
    пользователя и возможности подписки на любого пользователя.
    """
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (AllowAny,)
    pagination_class = LimitPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        if self.request.method in ('PUT', 'PATCH'):
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
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowUserSerializer(
            subscriptions, many=True,
            context={'request': request}
        )
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
                return Response(
                    SUBSCR_ALR_ERR, status=status.HTTP_400_BAD_REQUEST
                )
            if user == subscribed:
                return Response(
                    SUBSCR_NOT_YOURSELF_ERR, status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FollowUserSerializer(
                subscribed, context={'request': request}
            )
            Subscription.objects.create(user=user, subscribed=subscribed)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                SUBSCR_NOT_FOUND_ERR, status=status.HTTP_400_BAD_REQUEST
            )


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Tag. Выводит список тегов при GET-запросе."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Ingredient. Выводит список ингредиентов при
    GET-запросе. Поддерживается фильтрация по названию ингредиента.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Recipe. Присутствуют эндпоинты для добавления рецепта
    в избранное или в корзину а также для создания списка для покупок.
    """
    queryset = Recipe.objects.all()
    serializer_class = WriteRecipeSerializer
    permission_classes = (IsAuthorOrAdminOrJustReadingRecipe,)
    pagination_class = LimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def favorite_shopping_cart_handler(self, request, pk, model, serializer):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
            except ObjectDoesNotExist:
                return Response(
                    RECIPE_NOT_FOUND_ERR, status=status.HTTP_400_BAD_REQUEST
                )
            object = model.objects.filter(user=user, recipe=recipe)
            if object.exists():
                return Response(
                    RECIPE_ALR_ADDED_ERR, status=status.HTTP_400_BAD_REQUEST
                )
            serializer = serializer(recipe, context={'request': request})
            model.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            object = model.objects.filter(user=user, recipe=recipe)
            if object.exists():
                object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                RECIPE_NOT_ADDED_ERR, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.favorite_shopping_cart_handler(
            request, pk, FavoriteRecipe, FavoriteRecipeSerializer
        )

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.favorite_shopping_cart_handler(
            request, pk, ShoppingCart, ShoppingCartSerializer
        )

    @action(detail=False)
    def download_shopping_cart(self, request):
        return Response({'info': 'PDF'}, status=status.HTTP_200_OK)
