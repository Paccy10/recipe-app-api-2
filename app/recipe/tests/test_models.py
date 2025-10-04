from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from recipe.models import Recipe


class RecipeModelTests(TestCase):
    """Test Recipe model."""

    def test_create_recipe_succeeds(self):
        """Test creating a recipe"""

        user = get_user_model().objects.create_user("test@example.com", "testpass123")
        recipe = Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample recipe description",
        )

        self.assertEqual(str(recipe), recipe.title)
