from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from unittest.mock import patch

from recipe.models import Recipe, Tag, Ingredient, recipe_image_file_path


def create_user(email="user@example.com", password="testpass123"):
    """Create and return user"""

    return get_user_model().objects.create_user(email, password)


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

    @patch("recipe.models.uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""

        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = recipe_image_file_path(None, "myimage.jpg")

        self.assertEqual(file_path, f"uploads/recipe/{uuid}.jpg")


class TagModelTests(TestCase):
    """Test Tag model"""

    def test_create_tag_succeeds(self):
        """Test creating a tag"""

        user = create_user()
        tag = Tag.objects.create(user=user, name="tag1")

        self.assertEqual(str(tag), tag.name)


class IngredientModelTests(TestCase):
    """Test Ingredient model"""

    def test_create_ingredient_succeeds(self):
        """Test creating an ingredient"""

        user = create_user()
        ingredient = Ingredient.objects.create(user=user, name="ingredient1")

        self.assertEqual(str(ingredient), ingredient.name)
