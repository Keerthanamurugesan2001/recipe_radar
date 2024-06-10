"""
    This file contains the `Custom Middleware` configuration
"""

import logging
from django.http import JsonResponse
from recipe.utils import get_fail_response

logger = logger = logging.getLogger(__name__)


class RecipeRadarMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        logger.info(f"Request: {request.method} {request.get_full_path()}")

        response = self.get_response(request)

        logger.info(f"Response: {response.status_code}")

        return response

    def process_exception(self, request, exception):

        logger.critical(f"An error occurred: {exception}", exc_info=True)

        response = get_fail_response()
        response['message'] = str(exception)

        return JsonResponse(response, status=500)
