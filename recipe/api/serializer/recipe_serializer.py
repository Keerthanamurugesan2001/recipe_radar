from rest_framework import serializers
from recipe.models import Recipe, Category


class CreateRecipeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category_id = serializers.PrimaryKeyRelatedField(
            queryset=Category.objects.all(), source='category'
        )
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'category_id', 'avg_rating', 'user',
            'title', 'description', 'ingredients',
            'preparation_steps', 'cooking_time', 'serving_size'
        )
        read_only_fields = ('id',)

    def validate_title(self, value):
        if len(value) > 100:
            raise serializers.ValidationError(
                "Title cannot exceed 100 characters."
            )
        return value

    def validate_cooking_time(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Cooking time must be a positive integer."
            )
        return value

    def validate_serving_size(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Serving size must be at least 1."
            )
        return value

    def create(self, validated_data):
        recipe = Recipe.objects.create(**validated_data)
        return recipe


class ListRequestRecipeSerializer(serializers.Serializer):
    filters = serializers.JSONField(required=False)


class RecipeSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'


class UpdateRecipeSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(required=False)
    ingredients = serializers.CharField(required=False)
    preparation_steps = serializers.CharField(required=False)
    cooking_time = serializers.IntegerField(required=False)
    serving_size = serializers.IntegerField(required=False)
    category_id = serializers.PrimaryKeyRelatedField(
            queryset=Category.objects.all(), source='category', required=False
        )

    class Meta:
        model = Recipe
        fields = (
                    'id', 'user_id', 'title', 'description', 'ingredients',
                    'preparation_steps', 'cooking_time', 'serving_size',
                    'category_id'
                )