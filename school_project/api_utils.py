from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler ensuring unified JSON error format:
    Exposes both top-level keys (standard DRF) and an nested 'errors' dictionary
    to guarantee compatibility with existing API specifications and tests.
    """
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(response.data, dict):
            if 'errors' not in response.data:
                # Mirror errors inside 'errors' key
                errors_dict = {}
                for k, v in response.data.items():
                    if isinstance(v, list):
                        errors_dict[k] = [str(item) for item in v]
                    else:
                        errors_dict[k] = [str(v)]
                response.data = {
                    'errors': errors_dict,
                    **response.data
                }
        elif isinstance(response.data, list):
            response.data = {
                'errors': {'non_field_errors': [str(i) for i in response.data]},
                'detail': response.data
            }

    return response
