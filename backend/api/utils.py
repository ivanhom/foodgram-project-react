from recipes.models import RecipeIngredient


def add_ingredients_for_recipe(recipe_obj, ingredients):
    """Добавление списка ингредиентов в рецепт."""
    RecipeIngredient.objects.bulk_create(
        RecipeIngredient(
            recipe=recipe_obj,
            ingredient=ingredient['ingredient'],
            amount=ingredient['amount']
        ) for ingredient in ingredients)


def create_shopping_list(ingredients):
    """Формирует список ингредиентов к покупке."""
    message = (
        'Вас приветствует FOODGRAM!\n'
        'Вы сформировали список покупок для выбранных вами рецептов\n\n'
    )
    for ingredient in ingredients:
        message += (
            f' - {ingredient["ingredient__name"]} '
            f'--- {ingredient["total_amount"]}'
            f' {ingredient["ingredient__measurement_unit"]}\n'
        )
    message += '\nВаш продуктовый помощник FOODGRAM'

    return message
