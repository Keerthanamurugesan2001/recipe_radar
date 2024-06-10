from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
# Create your models here.


class RecipeBaseModelTemplate(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:

        abstract = True


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


class User(AbstractBaseUser, PermissionsMixin, RecipeBaseModelTemplate):

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def get_user_data_for_response(self) -> dict:
        """
            This method is used to get the user data in the format that
            is expected by the API.
        """
        user_data = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "is_active": self.is_active,
            "is_staff": self.is_staff,
            "date_joined": self.date_joined,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        return user_data

    class Meta:

        db_table = "tabUser"
        verbose_name = 'User'


class Category(RecipeBaseModelTemplate):

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:

        db_table = "tabCategory"
        verbose_name = 'Category'


class Recipe(RecipeBaseModelTemplate):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    ingredients = models.TextField()
    preparation_steps = models.TextField()
    cooking_time = models.IntegerField()
    serving_size = models.IntegerField()
    category = models.ForeignKey(
                                    Category,
                                    on_delete=models.SET_NULL,
                                    null=True
                                )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        db_table = "tabRecipe"
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'


class Review(RecipeBaseModelTemplate):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(
                                Recipe,
                                related_name='reviews',
                                on_delete=models.CASCADE
                            )
    rating = models.IntegerField()
    comment = models.TextField()

    def __str__(self) -> str:
        return f"{self.recipe.title} - {self.rating}"

    class Meta:
        db_table = "tabReview"
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
