[![Main Foodgram workflow](https://github.com/ivanhom/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/ivanhom/foodgram-project-react/actions/workflows/main.yml)


docker compose up -d && docker compose exec backend python manage.py migrate && docker compose exec backend python manage.py collectstatic --noinput && docker compose exec backend cp -r /app/collected_static/. /app/static/ && docker compose exec backend python manage.py upload_data_from_json && docker compose exec backend python manage.py createsuperuser --username admin --email admin@admin.ru






# Foodgram

### О возможностях проекта
«Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### О проекте
Проект развернут на удалённом сервере.
Для доступа к сайту можно перейти по ссылке: https://tregalex-kittygram.ddns.net

Проект развёрнут на Ubuntu 22.04.1 с использованием системы контейнеризации при помощи утилиты Docker Compose. Архитектура контейнеризации проекта поделена на отдельные зоны ответственности: backend, frontend, gateway и db.<br>
Статика для бэкенда и фронтенда, медиафайлы, а также база данных, расположены в отдельных томах (volume): static, media и pg_data, независимо от контейнеров.<br>
При изменениях кода в главной ветке (main) репозитория, произойдёт автоматическое тестирование кода на соответствие PEP8 и автоматическое развертывание новой версии на удалённом сервере с помощью GitHub Actions. При изменинии кода в любой другой ветке репозитория, произойдёт только автоматическое тестирование кода<br>

### Как самостоятельно развернуть проект
Для развертывания проекта необходимо в корневой директории проекта на удалённом сервере создать файл .env и добавить в него необходимые данные для переменных, по аналогии с файлом .env.example, который присутствует в репозитории.<br>
Дополнительно в корневую директорию необходимо скопировать файл docker-compose.production.yml из репозитория.<br>

Внимание! На удалённом сервере должны быть установлены утилиты Docker и Docker Compose.<br>

Запускаем Docker Compose на сервере:
```
sudo docker compose -f docker-compose.production.yml up -d
```
После запуска выполняем миграции, собираем статические файлы бэкенда и копируем их в /static/:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /app/static/
```
Наполняем базу данных заранее подготовленными данными (ингредиентами, тегами, пользователями)
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py upload_data_from_json
```
Создаём суперпользователя
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

### Для ревьювера
Адрес проекта: 
Адрес админ-панели проекта:
Адрес API документации проекта:

Username
```
admin
```
Email
```
admin@admin.ru
```
Password
```
I_am_admin2023
```
