import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient, Tag, User


class Command(BaseCommand):
    """Извлекает данные из JSON файлов и наполняет ими БД."""
    def db_objects_create(self, model, json_file):
        file = open(
            f'{settings.BASE_DIR}/data/{json_file}', 'r', encoding='utf-8'
        )
        json_data = file.read()
        data = json.loads(json_data)

        try:
            model.objects.bulk_create(
                model(**item) for item in data)
            print(f'БД пополнена списком {json_file}')
        except IntegrityError:
            print(f'Данные {json_file} уже есть в БД')

    def handle(self, *args, **kwargs):
        self.db_objects_create(Tag, 'tags.json')
        self.db_objects_create(Ingredient, 'ingredients.json')
        self.db_objects_create(User, 'users.json')
