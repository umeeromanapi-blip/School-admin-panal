from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    Root API Directory — School Management Admin Panel
    Provides browsable links to all available REST API endpoints.
    """
    return Response({
        'title': 'School Management Admin Panel REST API',
        'version': '1.0',
        'database': 'SQLite',
        'endpoints': {
            'students': request.build_absolute_uri('/api/students/'),
            'dashboard_stats': request.build_absolute_uri('/api/dashboard/stats/'),
            'teachers': request.build_absolute_uri('/api/teachers/'),
            'attendance': request.build_absolute_uri('/api/attendance/'),
            'fees': request.build_absolute_uri('/api/fees/'),
            'exams': request.build_absolute_uri('/api/exams/'),
            'announcements': request.build_absolute_uri('/api/announcements/'),
        }
    })
