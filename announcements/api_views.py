from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Announcement
from .serializers import AnnouncementSerializer


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_announcement_list_create(request):
    if request.method == 'GET':
        category = request.query_params.get('category', '').strip()
        audience = request.query_params.get('audience', '').strip()
        announcements = Announcement.objects.filter(is_active=True).order_by('-is_pinned', '-published_date')
        if category:
            announcements = announcements.filter(category=category)
        if audience:
            announcements = announcements.filter(audience=audience)
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = AnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def api_announcement_detail_update_delete(request, id):
    try:
        announcement = Announcement.objects.get(id=id)
    except Announcement.DoesNotExist:
        return Response({'error': 'Announcement not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(AnnouncementSerializer(announcement).data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        partial = (request.method == 'PATCH')
        serializer = AnnouncementSerializer(announcement, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        announcement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
