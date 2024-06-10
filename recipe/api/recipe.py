from rest_framework import status
from django.db.models import Avg, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from recipe.models import Recipe, Review
from recipe.api.filter import RecipeFilter
from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    GenericAPIView,
    RetrieveUpdateDestroyAPIView
)
from recipe.api.serializer import (
    CreateRecipeSerializer,
    RecipeSerializer,
    ListRequestRecipeSerializer,
    UpdateRecipeSerializer,
    ReviewSerializer
)
from recipe.utils import (
    get_success_response,
    get_fail_response,
    CustomPagination
)


class CreateRecipeAPI(CreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="Create Recipe",
        request_body=CreateRecipeSerializer,
        responses={201: CreateRecipeSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = get_success_response()
        response['message'] = "Recipe Created Successfully"
        response['data'] = serializer.data
        return Response(response, status=status.HTTP_201_CREATED)


class ListGetRecipeAPI(GenericAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="List Recipes",
        request_body=ListRequestRecipeSerializer,
        responses={200: RecipeSerializer(many=True)}
    )
    def post(self, request, *args, **kwargs):
        serializer = ListRequestRecipeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        filters = serializer.validated_data.get('filters', {})

        queryset = self.get_queryset()

        if filters:
            queryset = queryset.filter(**filters)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        response = get_success_response()
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            _response = paginator.get_paginated_response(serializer.data)
            response['message'] = "Fatched Successfully"
            response["data"] = _response.data
            return Response(response, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        response['message'] = "Recipes details"
        response['data'] = serializer.data
        return Response(response, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
                avg_rating=Avg('reviews__rating')
            )
        return queryset


class ListUpdateDeleteRecipeAPI(RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = UpdateRecipeSerializer
    permission_classes = [IsAuthenticated]

    def check_user_permission(self, request, recipe):
        if request.user.id != recipe.user_id:
            response = get_fail_response()
            response["message"] = "You are not authorized to perform this action on this recipe"
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        return None

    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="Update Recipe",
        request_body=UpdateRecipeSerializer,
        responses={200: UpdateRecipeSerializer}
    )
    def put(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        permission_response = self.check_user_permission(request, recipe)
        if permission_response:
            return permission_response
        response = super().update(request, *args, **kwargs)
        _response = get_success_response()
        _response['message'] = "Recipe Updated Successfully"
        _response['data'] = response.data
        return Response(_response, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="Delete Recipe",
    )
    def delete(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        permission_response = self.check_user_permission(request, recipe)
        if permission_response:
            return permission_response
        response = super().delete(request, *args, **kwargs)
        _response = get_success_response()
        _response['message'] = "Recipe Deleted Successfully"
        _response['data'] = response.data
        return Response(_response, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="Retrieve Recipe",
        responses={200: UpdateRecipeSerializer}
    )
    def get(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        reviews = Review.objects.filter(recipe_id=kwargs['pk']).select_related('user').annotate(
            first_name=F('user__first_name'),
            last_name=F('user__last_name')
        ).values('id', 'rating', 'comment', 'created_at', 'updated_at', 'first_name', 'last_name')

        recipe_data = self.get_serializer(recipe).data
        review_serializer = ReviewSerializer(reviews, many=True)

        response = get_success_response()
        response['data'] = {
            'recipe': recipe_data,
            'reviews': review_serializer.data
        }
        response['message'] = "Recipe Retrieved Successfully"
        return Response(response, status=status.HTTP_200_OK)
