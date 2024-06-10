import copy
import re
from recipe.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from recipe_radar.constant import RESPONSE_FAILED, RESPONSE_SUCCESS
from rest_framework.views import exception_handler
from rest_framework.serializers import ValidationError


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


def get_success_response() -> dict:
    """
        Returns a deep copy of the success response dictionary.

        This function returns a deep copy of the global RESPONSE_SUCCESS
        dictionary.The deep copy ensures that the returned dictionary can
        be modified without altering the original RESPONSE_SUCCESS dictionary.

        Returns:
            dict: A deep copy of the success response dictionary.
    """
    return copy.deepcopy(RESPONSE_SUCCESS)


def get_fail_response() -> dict:
    """
        Returns a deep copy of the success response dictionary.

        This function returns a deep copy of the global RESPONSE_FAILED
        dictionary.The deep copy ensures that the returned dictionary can be
        modified without altering the original RESPONSE_FAILED dictionary.

        Returns:
            dict: A deep copy of the success response dictionary.
    """
    return copy.deepcopy(RESPONSE_FAILED)


def recipe_custom_exc_handler(exc, context):
    """
        `Recipe Radar` app had some format of returning responses,
        so have to convert.
    """
    response = exception_handler(exc, context)

    if response is not None:
        _response = get_fail_response()

        try:
            if isinstance(exc, ValidationError):
                errors = []
                for error in response.data.values():
                    errors.append(error[0])
                _response['message'] = errors
            elif exc.status_code >= 400:
                _response['message'] = exc.default_detail
            else:
                _response['data'] = response.data
            response.data = _response
        except:
            _response["message"] = str(exc)
            response.data = _response

    return response


def validate_password(value) -> str:
    """
    Validates the strength and format of a password.

    Parameters:
    - value (str): The password to validate.

    Returns:
    - str: The validated password if it passes all validation checks.

    Raises:
    - ValidationError: If the password does not meet the specified criteria,
      including minimum length, inclusion of uppercase letters,
      lowercase letters, digits, and special characters.
    """
    min_length = 8
    if len(value) < min_length:
        raise ValidationError(
            f"Password must be at least {min_length} characters long."
        )
    if not any(char.isupper() for char in value):
        raise ValidationError(
            "Password must contain at least one uppercase letter."
        )
    if not any(char.islower() for char in value):
        raise ValidationError(
            "Password must contain at least one lowercase letter."
        )
    if not any(char.isdigit() for char in value):
        raise ValidationError(
            "Password must contain at least one digit."
        )
    if not any(char in "!@#$%^&*()-_=+{}[]|;:,.<>?`~" for char in value):
        raise ValidationError(
            "Password must contain at least one special character."
        )
    return value


def validate_phone_number(value) -> str:
    """
    Validates the format and uniqueness of a phone number.

    Parameters:
    - value (str): The phone number to validate.

    Returns:
    - str: The validated phone number if it passes all validation checks.

    Raises:
    - ValidationError: If the phone number format is invalid or if a user with
      the same phone number already exists in the database.
    """
    phone_number_regex = r'^\+?1?\d{9,15}$'
    if not re.match(phone_number_regex, value):
        raise ValidationError("Invalid phone number format")

    if User.objects.filter(phone_number=value).exists():
        raise ValidationError(
            "User with this phone number already exists."
        )
    return value


def validate_email(value) -> str:
    """
    Validates the format and uniqueness of an email address.

    Parameters:
    - value (str): The email address to validate.

    Returns:
    - str: The validated email address if it passes all validation checks.

    Raises:
    - ValidationError: If the email address format is invalid or if a user with
      the same email address already exists in the database.
    """
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if not re.match(email_regex, value):
        raise ValidationError("Invalid email format")
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            "User with this email already exists."
        )
    return value


def success_response(data=None, status=None, message="success"):
    response = get_success_response()
    response['data'] = data if data is not None else {}
    response['message'] = message
    return Response(response, status=status)
