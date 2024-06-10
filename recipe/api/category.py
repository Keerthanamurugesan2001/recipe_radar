from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from recipe.models import Category
from recipe.api.serializer import CategoryCreateSerializer, CategoryDetailSerializer
from drf_yasg.utils import swagger_auto_schema


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CategoryCreateSerializer
        return CategoryDetailSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST'] and not self.request.user.is_superuser:
            raise PermissionDenied("Only superusers can create categories.")
        return super().get_permissions()

    @swagger_auto_schema(
        tags=['Category'],
        operation_description="Create Category",
        request_body=CategoryCreateSerializer,
        responses={201: CategoryCreateSerializer}
    )
    def perform_create(self, serializer):
        serializer.save()


class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE'] and not self.request.user.is_superuser:
            raise PermissionDenied("Only superusers can update or delete categories.")
        return super().get_permissions()
    
    @swagger_auto_schema(
        tags=['Category'],
        operation_description="Update Category",
        request_body=CategoryDetailSerializer,
        responses={201: CategoryDetailSerializer}
    )
    def perform_update(self, serializer):
        serializer.save()

    @swagger_auto_schema(
        tags=['Category'],
        operation_description="Delete Category",
        request_body=CategoryDetailSerializer,
        responses={201: CategoryDetailSerializer}
    )
    def perform_destroy(self, instance):
        instance.delete()
