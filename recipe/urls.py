from django.urls import path
from recipe import api

urlpatterns = [
    path('signup', api.SignupAPI.as_view(), name='signup'),
    path('login', api.LoginAPI.as_view(), name='login'),
    path('recipe', api.CreateRecipeAPI.as_view(), name='recipe'),
    path('reviews', api.ReviewCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>', api.ReviewDetailView.as_view(), name='review-detail'),
    path('categories', api.CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('categories/<int:pk>', api.CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category-retrieve-update-destroy'),
    path('recipes', api.ListGetRecipeAPI.as_view(), name='list-recipes'),
    path('recipe/<int:pk>', api.ListUpdateDeleteRecipeAPI.as_view(), name='update-recipe'),
    path('search/<str:query>', api.SearchAPI.as_view(), name='search'),
]
