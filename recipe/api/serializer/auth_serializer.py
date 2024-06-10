from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from recipe.models import User
from recipe.utils import (
    validate_phone_number,
    validate_password,
    validate_email
)


class SignupSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
                    "first_name", "last_name",
                    "phone_number", 'email', 'password',
                )

    def validate_email(self, value):
        validate_email(value)
        return value

    def validate_phone_number(self, value):
        validate_phone_number(value)
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Check if the user exists and provided correct credentials
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")

        return attrs
