"""
Tests for recipe APIs
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from recipe.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailsSerializer

RECIPES_URL = reverse("recipe:recipe-list")


def create_recipe(user, **params):
    """Create and return a sample recipe"""

    defaults = {
        "title": "Sample recipe title",
        "time_minutes": 22,
        "price": Decimal("5.25"),
        "description": "Sample description",
        "link": "http://example.com/recipe.pdf",
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)

    return recipe


def get_recipe_detail_url(recipe_id):
    """Create and return a recipe detail URL"""

    return reverse("recipe:recipe-detail", args=[recipe_id])


def create_user(**params):
    """Create and return a new user"""

    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_fails(self):
        """Test auth is required to call API"""

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="testpass123")
        self.client.force_authenticate(self.user)

    def test_get_recipes_succeeds(self):
        """Test get a list of recipes"""

        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_user_recipes_succeeds(self):
        """Test get authenticated user recipes"""

        other_user = create_user(email="other@example.com", password="pass1234")
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_details_succeeds(self):
        """Test get recipe details"""

        recipe = create_recipe(user=self.user)
        url = get_recipe_detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailsSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_succeeds(self):
        """Test creating a recipe"""

        payload = {
            "title": "New recipe",
            "time_minutes": 30,
            "price": Decimal("5.99"),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe_succeeds(self):
        """Test partial update recipe"""

        original_link = "https://example.come/recipe.pdf"
        recipe = create_recipe(
            user=self.user, title="Sample recipe", link=original_link
        )
        url = get_recipe_detail_url(recipe.id)
        payload = {"title": "Updated recipe title"}
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_update_recipe_succeeds(self):
        """Test full update of recipe"""

        recipe = create_recipe(
            user=self.user,
            title="Sample recipe",
            link="https://example.come/recipe.pdf",
            description="Sample recipe description",
        )
        payload = {
            "title": "Update recipe title",
            "link": "https://example.come/updated-recipe.pdf",
            "description": "Updated recipe description",
            "time_minutes": 10,
            "price": Decimal("2.50"),
        }
        url = get_recipe_detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_update_recipe_user_fails(self):
        """Test changing the recipe user results in error"""

        new_user = create_user(email="new_user@example.com", password="test1234")
        recipe = create_recipe(user=self.user)
        payload = {"user": new_user.id}
        url = get_recipe_detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe_succeeds(self):
        """Test deleting recipe"""

        recipe = create_recipe(user=self.user)
        url = get_recipe_detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_user_recipe_fails(self):
        """Test deleting other user recipe gives an error"""

        new_user = create_user(email="user2@example.com", password="test1234")
        recipe = create_recipe(user=new_user)
        url = get_recipe_detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
