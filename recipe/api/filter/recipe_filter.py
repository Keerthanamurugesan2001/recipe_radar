from django_filters import rest_framework as filters
from recipe.models import Recipe


class RecipeFilter(filters.FilterSet):
    avg_rating = filters.NumberFilter(field_name='avg_rating')
    title = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    ingredients = filters.CharFilter(lookup_expr='icontains')
    preparation_steps = filters.CharFilter(lookup_expr='icontains')
    cooking_time = filters.NumberFilter()
    serving_size = filters.NumberFilter()
    category_id = filters.NumberFilter(field_name='category__id')

    class Meta:
        model = Recipe
        fields = ['avg_rating', 'title', 'description', 'ingredients',
                  'preparation_steps', 'cooking_time', 'serving_size',
                  'category_id']
