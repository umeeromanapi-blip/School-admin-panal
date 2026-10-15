from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Teacher
from .serializers import TeacherSerializer


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_teacher_list_create(request):
    if request.method == 'GET':
        query = request.query_params.get('q', '').strip()
        dept = request.query_params.get('dept', '').strip()
        teachers = Teacher.objects.all().order_by('-created_at')
        if query:
            teachers = teachers.filter(
                Q(full_name__icontains=query) |
                Q(employee_id__icontains=query) |
                Q(subject__icontains=query)
            )
        if dept:
            teachers = teachers.filter(department=dept)
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = TeacherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def api_teacher_detail_update_delete(request, id):
    try:
        teacher = Teacher.objects.get(id=id)
    except Teacher.DoesNotExist:
        return Response({'error': 'Teacher not found', 'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(TeacherSerializer(teacher).data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        partial = (request.method == 'PATCH')
        serializer = TeacherSerializer(teacher, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        teacher.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
