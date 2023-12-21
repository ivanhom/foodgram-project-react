from django.urls import include, path
from rest_framework import routers

from api.views import (IngredientViewSet, RecipeViewSet,  # isort:skip
                       TagViewSet, UsersViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register(r'users', UsersViewSet)
router_v1.register(r'tags', TagViewSet)
router_v1.register(r'ingredients', IngredientViewSet)
router_v1.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
