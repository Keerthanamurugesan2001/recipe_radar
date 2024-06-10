from rest_framework import serializers
from recipe.models import Review, Recipe


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    recipe = serializers.ReadOnlyField(source='recipe.title')

    class Meta:
        model = Review
        fields = ['id', 'user', 'recipe', 'rating', 'comment']
        read_only_fields = ['user', 'recipe']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    

class ReviewCreateSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    recipe_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = ['user', 'recipe_id', 'id', 'recipe', 'rating', 'comment']
        read_only_fields = ['user', 'recipe']

    def create(self, validated_data):
        recipe_id = validated_data.pop('recipe_id')
        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError("Recipe does not exist.")

        review = Review.objects.create(recipe=recipe, **validated_data)
        return review
