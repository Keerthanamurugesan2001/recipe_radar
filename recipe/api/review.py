from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers

from recipe.models import Review, Recipe
from recipe.api.serializer import ReviewSerializer, ReviewCreateSerializer
from recipe.api.permission import IsOwnerOrReadOnly



class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        tags=['Review'],
        operation_description="Create Review",
        request_body=ReviewCreateSerializer,
        responses={201: ReviewCreateSerializer}
    )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]

    @swagger_auto_schema(
        tags=['Review'],
        operation_description="Update Review",
        request_body=ReviewSerializer,
        responses={201: ReviewSerializer}
    )
    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this review.")
        super().perform_update(serializer)

    @swagger_auto_schema(
        tags=['Review'],
        operation_description="Delete Review",
        request_body=ReviewSerializer,
        responses={201: ReviewSerializer}
    )
    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this review.")
        super().perform_destroy(instance)