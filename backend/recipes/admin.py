from django import forms
from django.contrib import admin

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)


admin.site.empty_value_display = '--пусто--'


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_display_links = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    list_display_links = ('name',)


class IngredientsFormsSet(forms.models.BaseInlineFormSet):
    def clean(self) -> None:
        super().clean()
        amount = 0
        for form in self.forms:
            if (form.cleaned_data.get('amount') and not
                    form.cleaned_data.get('DELETE')):
                amount += form.cleaned_data['amount']
        if amount == 0:
            raise forms.ValidationError(
                'В рецепте должен быть минимум 1 ингредиент!'
            )


class IngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    formset = IngredientsFormsSet
    min_num = 1
    extra = 2


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'email', 'pub_date', 'tag')
    list_filter = ('tags__name',)
    search_fields = ('name', 'author__username', 'author__email')
    list_display_links = ('name',)
    readonly_fields = ('favorite',)
    fields = (('name', 'cooking_time'),
              'text', 'image',
              ('tags', 'author'),
              'favorite')
    inlines = (IngredientsInline,)

    def email(self, obj):
        return obj.author.email
    email.short_description = 'Email'

    def favorite(self, obj):
        return obj.favorite.count()
    favorite.short_description = 'Раз добавлено в избранное'

    def tag(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])
    tag.short_description = 'Теги'


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'amount', 'recipe', 'tags')
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('recipe__tags__name', 'ingredient__measurement_unit')
    list_display_links = ('ingredient',)

    def tags(self, obj):
        return ', '.join([tag.name for tag in obj.recipe.tags.all()])
    tags.short_description = 'Теги'


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'recipe', 'tags')
    search_fields = ('user__username', 'user__email', 'recipe__name')
    list_filter = ('recipe__tags__name',)

    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'

    def tags(self, obj):
        return ', '.join([tag.name for tag in obj.recipe.tags.all()])
    tags.short_description = 'Теги'


class ShoppingCartAdmin(FavoriteRecipeAdmin):
    pass


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
