from django.conf import settings

USER_CREATE_CHAR_ERR = 'Недопустимый символ в имени пользователя'
USER_CREATE_EXIST_EMAIL_ERR = 'Пользователь с таким email уже зарегистрирован'
USER_CREATE_EXIST_NAME_ERR = 'Такое имя пользователя уже существует'
USER_CREATE_ME_ERR = (
    f'Запрещено использовать имя {settings.USER_INFO_URL_PATH}'
)
INVALID_TOKEN_ERR = 'Код подтверждения недействителен'
REVIEW_CREATE_EXIST_ERR = 'Вы уже оставляли отзыв на это произведение'
