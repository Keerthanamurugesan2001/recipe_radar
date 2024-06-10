from rest_framework import serializers
from recipe.models import Category


class CategoryCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

    def create(self, validated_data):
        return Category.objects.create(**validated_data)
    

class CategoryDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance