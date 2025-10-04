"""
Recipe APIs Serializers
"""

from rest_framework import serializers

from recipe.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Recipe serializer"""

    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link"]
        read_only_fields = ["id"]


class RecipeDetailsSerializer(RecipeSerializer):
    """serializer for recipe details view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]
