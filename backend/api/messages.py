from django.conf import settings

INGRED_REPEAT_ERR = {
    'ingredients': 'Ингредиенты в списке не должны повторяться!'
}
INGRED_NOT_FOUND_ERR = {
    'ingredients': 'У рецепта должен быть минимум 1 ингредиент!'
}
INGRED_AMOUNT_ERR = (
    'Количество ингредиента должно быть от '
    f'{settings.INGRED_MIN_AMOUNT} до {settings.INGRED_MAX_AMOUNT}'
)

COOKING_TIME_ERR = (
    'Время приготовления должно быть от '
    f'{settings.COOKING_MIN_TIME} до {settings.COOKING_MAX_TIME}'
)

TAG_REPEAT_ERR = {
    'tags': 'Теги в списке не должны повторяться!'
}
TAG_NOT_FOUND_ERR = {'tags': 'У рецепта должен быть минимум 1 тег!'}

RECIPE_ALR_ADDED_ERR = {'errors': 'Вы уже добавили данный рецепт!'}
RECIPE_NOT_ADDED_ERR = {'errors': 'Вы не добавляли данный рецепт!'}

SUBSCR_ALR_ERR = {'errors': 'Вы уже подписаны на данного пользователя!'}
SUBSCR_NOT_YOURSELF_ERR = {'errors': 'Нельзя подписаться на самого себя!'}
SUBSCR_NOT_FOUND_ERR = {
    'errors': 'Вы не были подписаны на этого пользователя!'
}
