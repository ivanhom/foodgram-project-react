# Generated by Django 3.2.3 on 2023-12-31 15:49

from django.db import migrations, models
import recipes.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20240101_0028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[recipes.validators.MinMaxValidator(max_value=600, message='Время приготовления должно быть от 1 до 600', min_value=1)], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[recipes.validators.MinMaxValidator(max_value=10000, message='Количество ингредиента должно быть от 1 до 10000', min_value=1)], verbose_name='Количество'),
        ),
    ]
