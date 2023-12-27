from recipes.models import RecipeIngredient


def add_ingredients_for_recipe(recipe_obj, ingredients):
    """Добавление списка ингредиентов в рецепт."""
    RecipeIngredient.objects.bulk_create(
        RecipeIngredient(
            recipe=recipe_obj,
            ingredient=ingredient['ingredient'],
            amount=ingredient['amount']
        ) for ingredient in ingredients)
