from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from recipe.models import Recipe
from recipe.api.serializer import RecipeSerializer
from recipe.utils import get_fail_response, get_success_response


class SearchAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeSerializer

    @swagger_auto_schema(
        tags=['Search & Filter'],
        operation_description="Search API",
        responses={200: RecipeSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        query = kwargs.get('query', None)

        if query:
            search_results = Recipe.objects.filter(
                Q(title__icontains=query) |
                Q(category__name__icontains=query) |
                Q(description__icontains=query) |
                Q(ingredients__icontains=query) |
                Q(cooking_time__icontains=query) |
                Q(serving_size__icontains=query)
            ).distinct()

            if search_results.exists():
                serializer = self.get_serializer(search_results, many=True)
                response = get_success_response()
                response['data']['search_results'] = serializer.data
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = get_fail_response()
                response['message'] = "No results found"
                return Response(response, status=status.HTTP_404_NOT_FOUND)
        else:
            response = get_fail_response()
            response['message'] = "Please enter a search query"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
