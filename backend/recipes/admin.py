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
    list_filter = ('name',)
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
    list_display = ('id', 'name', 'author', 'pub_date')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author')
    list_display_links = ('name',)
    readonly_fields = ('favorite',)
    fields = (('name', 'cooking_time'),
              'text', 'image',
              ('tags', 'author'),
              'favorite')
    inlines = (IngredientsInline,)

    def favorite(self, object):
        return object.favorite.count()
    favorite.short_description = 'Раз добавлено в избранное'


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'amount', 'recipe')
    search_fields = ('recipe', 'ingredient')
    list_filter = ('recipe',)
    list_display_links = ('ingredient',)


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
